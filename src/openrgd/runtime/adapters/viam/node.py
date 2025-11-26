"""
OPENRGD RUNTIME ADAPTER: VIAM ROBOTICS
--------------------------------------------------------------------------------
This module provides the connection layer between the OpenRGD Cognitive Engine
and the Viam Robotics platform (viam.com).

PREREQUISITES:
1. Install Viam SDK:
   $ pip install viam-sdk

2. Set Environment Variables (or provide via config):
   - VIAM_ADDRESS: The robot's address (e.g., 'my-robot.viam.cloud' or 'localhost:8080')
   - VIAM_SECRET:  The robot's secret API key (from Viam app > Connect tab)

USAGE:
   The adapter is loaded by 'rgd run viam'. It maps RGD 'hal_mapping'
   components to Viam resources and synchronizes state in real-time.
--------------------------------------------------------------------------------
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional

# Viam SDK Imports (Must be installed)
try:
    from viam.robot.client import RobotClient
    from viam.rpc.dial import DialOptions
    from viam.components.motor import Motor
    from viam.components.camera import Camera
    from viam.components.sensor import Sensor
    from viam.components.base import Base
except ImportError:
    print("CRITICAL: 'viam-sdk' not found. Please run: pip install viam-sdk")
    raise

from ....core.visuals import log
from ..base import BaseAdapter

class ViamAdapter(BaseAdapter):
    """
    The Cloud-Native Connector.
    Connects OpenRGD to any Viam-compatible robot via gRPC.
    """
    def __init__(self, engine):
        super().__init__(engine)
        self.robot: Optional[RobotClient] = None
        self.parts: Dict[str, Any] = {} # Cache of connected Viam components
        
        # Connection Configuration (from Env Vars)
        self.address = os.getenv("VIAM_ADDRESS", "localhost:8080")
        self.secret = os.getenv("VIAM_SECRET", "")
        
    async def connect(self):
        """Establish secure gRPC tunnel to the robot."""
        log(f"Dialing Viam Robot at {self.address}...", "SYSTEM")
        
        # Connection options
        opts = RobotClient.Options(
            refresh_interval=0, # We manage polling manually
            dial_options=DialOptions(
                credentials=None if not self.secret else \
                    DialOptions.Credentials(type="robot-location-secret", payload=self.secret),
                insecure=not self.secret # If no secret, assume insecure/local connection
            )
        )
        
        try:
            self.robot = await RobotClient.at_address(self.address, opts)
            log("Viam Uplink Established.", "SUCCESS")
            await self._map_components()
        except Exception as e:
            log(f"Viam Connection Failed: {e}", "ERROR")
            raise e

    async def _map_components(self):
        """
        Reads the RGD 'hal_mapping.jsonc' and discovers matching Viam components.
        """
        # Retrieve hardware definitions from the Engine
        hal = self.engine.hal.get("actuator_drivers_map", {})
        sensors = self.engine.hal.get("sensor_drivers_map", {})
        
        # Merge maps to scan all hardware
        all_devices = {**hal, **sensors}
        
        count = 0
        for rgd_id, config in all_devices.items():
            # MAPPING LOGIC:
            # RGD "hardware_uid_str" corresponds to Viam's "Component Name"
            viam_name = config.get("hardware_uid_str")
            if not viam_name: continue
            
            try:
                part = None
                # Heuristic type matching based on RGD ID conventions
                # In v1.0 this should use explicit type fields from the spec
                if "camera" in rgd_id:
                    part = Camera.from_robot(self.robot, viam_name)
                elif "motor" in rgd_id or "joint" in rgd_id:
                    part = Motor.from_robot(self.robot, viam_name)
                elif "base" in rgd_id:
                    part = Base.from_robot(self.robot, viam_name)
                elif "sensor" in rgd_id:
                    part = Sensor.from_robot(self.robot, viam_name)
                
                if part:
                    self.parts[rgd_id] = part
                    count += 1
                    log(f"Linked [Viam] {viam_name} -> [RGD] {rgd_id}", "DEBUG")
                    
            except Exception:
                log(f"Component not found on robot: {viam_name}", "WARN")
        
        log(f"Mapped {count} hardware components via Viam API.", "SUCCESS")

    def spin(self):
        """Main Async Loop Entry Point."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.connect())
            loop.run_until_complete(self._lifecycle_loop())
        except KeyboardInterrupt:
            log("Closing Viam Uplink...", "SYSTEM")
            if self.robot:
                loop.run_until_complete(self.robot.close())
        finally:
            loop.close()

    async def _lifecycle_loop(self):
        """The Cognitive Heartbeat (Target: 10Hz)."""
        while True:
            start_time = asyncio.get_event_loop().time()
            
            # 1. SENSE PHASE (Parallel Data Gathering)
            await self._sense_phase()
            
            # 2. THINK PHASE (Synchronous Logic - Placeholder)
            # self.engine.update() 
            
            # 3. ACT PHASE (Parallel Dispatch - Placeholder)
            # await self._act_phase()
            
            # Frequency Maintenance
            elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = max(0, 0.1 - elapsed) # 100ms target
            await asyncio.sleep(sleep_time)

    async def _sense_phase(self):
        """Pull data from all connected sensors in parallel."""
        tasks = []
        ids = []
        
        for rgd_id, part in self.parts.items():
            if isinstance(part, Motor):
                tasks.append(part.get_position())
                ids.append((rgd_id, "position"))
            elif isinstance(part, Camera):
                # Skip cameras on every tick to save bandwidth
                pass 

        if not tasks: return

        # Execute all RPC calls concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (rgd_id, type_), res in zip(ids, results):
            if isinstance(res, Exception):
                continue
            
            # Inject data into the RGD World Model state
            if self.engine.state.get("world_model") is None:
                self.engine.state["world_model"] = {}
                
            self.engine.state["world_model"][rgd_id] = {type_: res}

    def publish_intent(self, intent):
        """Translates RGD Intent into Viam Commands (TODO)."""
        # Example: await part.go_to(intent['target'])
        pass