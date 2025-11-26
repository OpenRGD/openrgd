from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import entry_points
from typing import Callable, List

import typer

from .visuals import log
from .plugins_policy import (
    PluginPolicy,
    load_plugin_policy,
    evaluate_external_plugin,
)

# Type alias for plugin attach functions
CommandAttachFn = Callable[[typer.Typer], None]


@dataclass
class CommandPlugin:
    name: str
    attach: CommandAttachFn
    description: str | None = None
    source: str = "builtin"  # "builtin" | "external"
    policy_status: str = "allowed"  # allowed | blocked | unlisted_allowed | unlisted_blocked


# Internal command modules that ship with OpenRGD
BUILTIN_COMMAND_MODULES = [
    "openrgd.commands.compiler",
    "openrgd.commands.integrity",
    "openrgd.commands.plugins",  # plugin manager itself
    # Add more built-in command modules here as the project grows
]


def load_builtin_plugins() -> List[CommandPlugin]:
    """Load internal command plugins defined in this repository."""
    plugins: List[CommandPlugin] = []

    for mod_path in BUILTIN_COMMAND_MODULES:
        try:
            mod = import_module(mod_path)
        except Exception as e:
            log(f"Failed to import builtin command module '{mod_path}': {e}", "ERROR")
            continue

        if not hasattr(mod, "attach"):
            # Module does not expose the plugin API, skip it
            log(f"Builtin module '{mod_path}' has no attach() function. Skipped.", "WARN")
            continue

        name = getattr(mod, "PLUGIN_NAME", mod_path.split(".")[-1])

        def _make_attach(m):
            def _attach(app: typer.Typer) -> None:
                m.attach(app)
            return _attach

        plugins.append(
            CommandPlugin(
                name=name,
                attach=_make_attach(mod),
                description=getattr(mod, "__doc__", None),
                source="builtin",
                policy_status="allowed",
            )
        )

    return plugins


def load_external_plugins(policy: PluginPolicy) -> List[CommandPlugin]:
    """
    Load external plugins discovered via Python entry points.

    Any installed package can register commands by declaring an entry point
    in the `rgd.commands` group that points to an `attach(root_app)` function.
    """
    plugins: List[CommandPlugin] = []

    try:
        eps = entry_points(group="rgd.commands")
    except TypeError:
        all_eps = entry_points()
        eps = all_eps.get("rgd.commands", [])

    for ep in eps:
        plugin_name = ep.name  # e.g. "rgd-timetravel"
        allowed, status = evaluate_external_plugin(plugin_name, policy)

        if not allowed:
            log(f"External plugin '{plugin_name}' blocked by policy ({status}).", "WARN")
            continue

        if status == "unlisted_allowed":
            log(
                f"External plugin '{plugin_name}' is not in allowlist but is being "
                "loaded at your own risk (unlisted_allowed).",
                "WARN",
            )

        try:
            attach_fn = ep.load()
        except Exception as e:
            log(f"Failed to load external plugin '{plugin_name}': {e}", "ERROR")
            continue

        def _make_attach(fn: CommandAttachFn):
            def _attach(app: typer.Typer) -> None:
                fn(app)
            return _attach

        plugins.append(
            CommandPlugin(
                name=plugin_name,
                attach=_make_attach(attach_fn),
                description=None,
                source="external",
                policy_status=status,
            )
        )

    return plugins


def register_all_plugins(app: typer.Typer) -> None:
    """
    Attach all built-in and external command plugins to the root Typer app,
    honoring the plugin policy defined in plugins.toml (if present).
    """
    policy = load_plugin_policy()

    builtin_plugins = load_builtin_plugins()
    external_plugins = load_external_plugins(policy)

    for plugin in builtin_plugins + external_plugins:
        plugin.attach(app)
        log(
            f"Command group '{plugin.name}' registered "
            f"({plugin.source}, policy={plugin.policy_status}).",
            "DEBUG",
        )
