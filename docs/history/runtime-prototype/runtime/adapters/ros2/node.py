import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

# Mappa dinamica dei tipi di messaggio supportati
# Possiamo espanderla o usare import dinamico (importlib) per supportare tutto
from sensor_msgs.msg import Image, Imu, JointState, LaserScan
from std_msgs.msg import String, Float32

from ....core.visuals import log

MSG_TYPE_MAP = {
    "sensor_msgs/Image": Image,
    "sensor_msgs/Imu": Imu,
    "sensor_msgs/JointState": JointState,
    "sensor_msgs/LaserScan": LaserScan,
    "std_msgs/String": String
}

class ROS2Adapter(Node):
    """
    The somatic interface for ROS 2.
    Reflects the RGD 'hal_mapping' into real ROS subscribers/publishers.
    """
    def __init__(self, engine):
        super().__init__('openrgd_runtime_node')
        self.engine = engine
        self.subscriptions_list = []
        
        self._configure_perception()
        self._configure_actuation()

    def _configure_perception(self):
        """
        Reads 'hal_mapping.jsonc' -> 'sensor_drivers_map'
        and creates subscribers for every sensor defined.
        """
        hal = self.engine.hal # Il dizionario caricato dal JSON
        if not hal: return

        sensors = hal.get("sensor_drivers_map", {})
        count = 0
        
        for sensor_id, config in sensors.items():
            protocol = config.get("communication_protocol_enum")
            
            # Se il sensore usa ROS2
            if protocol == "ROS2_TOPIC":
                topic = config.get("stream_uri_str")
                msg_type_str = config.get("data_type_str")
                
                if topic and msg_type_str in MSG_TYPE_MAP:
                    msg_type = MSG_TYPE_MAP[msg_type_str]
                    
                    # Creiamo una callback che sa chi è (Closure)
                    # Inietta il dato direttamente nel cervello (engine)
                    def callback(msg, sid=sensor_id):
                        self.engine.ingest_sense(sid, msg)

                    sub = self.create_subscription(
                        msg_type,
                        topic,
                        callback,
                        10 # QoS Default
                    )
                    self.subscriptions_list.append(sub)
                    log(f"Connected Eye: {sensor_id} -> {topic}", "DEBUG")
                    count += 1
                else:
                    log(f"Unknown message type for {sensor_id}: {msg_type_str}", "WARN")
        
        if count > 0:
            log(f"Perception System Online: {count} sensors active.", "SUCCESS")

    def _configure_actuation(self):
        # Simile a sopra, ma crea Publishers per i comandi
        pass