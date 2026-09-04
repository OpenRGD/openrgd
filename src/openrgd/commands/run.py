"""Fail-closed compatibility boundary for external embodied runtimes."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import typer

app=typer.Typer(help="Embodied-runtime compatibility status. This canonical package does not actuate hardware.",no_args_is_help=True)
_RUNTIME_STATUS:dict[str,Any]={"schema_version":"1.0.0","component":"embodied-runtime","canonical_root":"OpenRGD/openrgd","status":"EXTERNAL_COMPONENT_REQUIRED","physical_actuation_available":False,"contract_package":"contracts/agent/v0.1.0","implementation_repository":None}

def _mode(output:str)->str:
    v=output.strip().lower()
    if v not in {"text","json"}: raise typer.BadParameter("output must be 'text' or 'json'")
    return v

def _emit(payload,output,*,error=False):
    if _mode(output)=="json": typer.echo(json.dumps(payload,sort_keys=True),err=error); return
    typer.echo(f"Embodied runtime: {payload['status']}",err=error)
    typer.echo("Physical actuation in canonical toolchain: disabled",err=error)

def _blocked(adapter:str,output:str,**context):
    payload={**_RUNTIME_STATUS,"requested_adapter":adapter,"outcome":"BLOCKED","reason":"EXTERNAL_EMBODIED_RUNTIME_REQUIRED",**context}
    _emit(payload,output,error=True); raise typer.Exit(2)

@app.command("status")
def status(output:str=typer.Option("text","--output","-o")):_emit(dict(_RUNTIME_STATUS),output)
@app.command("ros2")
def ros2(kernel_path:Path=typer.Option(Path("spec/00_core/kernel.jsonc"),"--kernel","-k"),output:str=typer.Option("text","--output","-o")):_blocked("ros2",output,requested_kernel=str(kernel_path))
@app.command("viam")
def viam(output:str=typer.Option("text","--output","-o")):_blocked("viam",output)
@app.command("hybrid")
def hybrid(output:str=typer.Option("text","--output","-o")):_blocked("hybrid",output)
