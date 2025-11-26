"""
OpenRGD Plugin Manager

This command group lets you inspect and update the plugin policy:
- list currently discoverable plugins and their policy status
- allow or block specific external plugins by name
- run diagnostics on the plugin configuration (doctor)

It acts as a control panel for the Cognitive BIOS extension layer.
"""

from __future__ import annotations

from typing import List

import typer
from importlib.metadata import entry_points

from ..core.plugins_policy import (
    load_plugin_policy,
    save_plugin_policy,
    evaluate_external_plugin,
)
from ..core.visuals import log

app = typer.Typer(
    help=(
        "Manage RGD plugins and plugin policy.\n\n"
        "Core commands:\n"
        "  rgd plugins list    → show discovered plugins and policy status\n"
        "  rgd plugins allow   → add a plugin to the allowlist\n"
        "  rgd plugins block   → add a plugin to the blocklist\n"
        "  rgd plugins doctor  → diagnose configuration issues\n\n"
        "Additional commands may appear as more tooling is added."
    )
)

PLUGIN_NAME = "plugins"


def _get_external_plugin_names() -> List[str]:
    """Return the list of discovered external plugin entry point names."""
    try:
        eps = entry_points(group="rgd.commands")
    except TypeError:
        all_eps = entry_points()
        eps = all_eps.get("rgd.commands", [])
    return sorted(ep.name for ep in eps)


@app.command("list")
def list_plugins():
    """
    List all discovered external plugins and show how the current policy treats them.
    """
    policy = load_plugin_policy()
    log("Inspecting plugin landscape according to plugins.toml ...", "SYSTEM")

    external_names = _get_external_plugin_names()
    if not external_names:
        log("No external plugins discovered (group 'rgd.commands' is empty).", "WARN")
    else:
        log(f"Discovered {len(external_names)} external plugin(s).", "DEBUG")

    # Core commands (builtin groups)
    if policy.core_commands:
        typer.echo("\n[CORE COMMAND GROUPS]")
        for name in sorted(policy.core_commands):
            typer.echo(f"  - {name} (builtin)")
    else:
        typer.echo("\n[CORE COMMAND GROUPS]")
        typer.echo("  (none explicitly defined in plugins.toml)")

    # External plugins
    typer.echo("\n[EXTERNAL PLUGINS]")
    if not external_names:
        typer.echo("  (no external plugins found)")
    else:
        for name in external_names:
            allowed, status = evaluate_external_plugin(name, policy)
            mark = "✓" if allowed else "✗"
            typer.echo(f"  {mark} {name}  [policy={status}]")

    typer.echo("")


@app.command("allow")
def allow_plugin(
    plugin_name: str = typer.Argument(
        ...,
        help="Name of the external plugin, e.g. 'rgd-timetravel'.",
    ),
):
    """
    Add a plugin to the allowlist in plugins.toml.
    """
    policy = load_plugin_policy()

    if plugin_name in policy.allowed:
        log(f"Plugin '{plugin_name}' is already in the allowlist.", "WARN")
        raise typer.Exit(0)

    policy.allowed.add(plugin_name)
    if plugin_name in policy.blocked:
        policy.blocked.discard(plugin_name)

    save_plugin_policy(policy)
    log(f"Plugin '{plugin_name}' added to allowlist.", "SUCCESS")


@app.command("block")
def block_plugin(
    plugin_name: str = typer.Argument(
        ...,
        help="Name of the external plugin, e.g. 'rgd-chaoslab'.",
    ),
):
    """
    Add a plugin to the blocklist in plugins.toml.
    """
    policy = load_plugin_policy()

    if plugin_name in policy.blocked:
        log(f"Plugin '{plugin_name}' is already in the blocklist.", "WARN")
        raise typer.Exit(0)

    policy.blocked.add(plugin_name)
    if plugin_name in policy.allowed:
        policy.allowed.discard(plugin_name)

    save_plugin_policy(policy)
    log(f"Plugin '{plugin_name}' added to blocklist.", "SUCCESS")


@app.command("doctor")
def doctor():
    """
    Run a diagnostic pass on the plugin configuration.

    Highlights:
    - allowed plugins that are not installed
    - installed plugins that are not in the allowlist
    - entries that appear in both allowed and blocked lists
    """
    policy = load_plugin_policy()
    external_names = set(_get_external_plugin_names())

    typer.echo("\n[PLUGIN POLICY DOCTOR]")
    typer.echo(f"Mode: {policy.mode}")
    typer.echo(f"Strict environment: {policy.strict_environment}")
    typer.echo(f"Allow unlisted at own risk: {policy.allow_unlisted_at_own_risk}")
    typer.echo("")

    allowed = set(policy.allowed)
    blocked = set(policy.blocked)

    # 1) Conflicts: plugins present in both allowed and blocked
    conflicts = allowed & blocked
    typer.echo("[CONFLICTS]")
    if conflicts:
        for name in sorted(conflicts):
            typer.echo(f"  ! {name} is present in both allowlist and blocklist.")
        typer.echo("  → Doctor recommendation: remove it from one of the lists.")
    else:
        typer.echo("  No allow/block conflicts detected.")

    # 2) Allowed but not installed
    typer.echo("\n[ALLOWED BUT NOT INSTALLED]")
    missing = allowed - external_names
    if missing:
        for name in sorted(missing):
            typer.echo(f"  - {name} (listed in allowlist, but not installed)")
    else:
        typer.echo("  All allowed plugins are installed (or allowlist is empty).")

    # 3) Installed but not in allowlist (only relevant in allowlist mode)
    typer.echo("\n[INSTALLED BUT UNLISTED]")
    if policy.mode == "allowlist":
        unlisted = external_names - allowed
        if unlisted:
            for name in sorted(unlisted):
                allowed_flag, status = evaluate_external_plugin(name, policy)
                typer.echo(
                    f"  - {name} (policy={status}, "
                    f"{'loaded' if allowed_flag else 'blocked'})"
                )
        else:
            typer.echo("  No unlisted installed plugins.")
    else:
        typer.echo("  Mode is not 'allowlist'; unlisted plugins are not strictly relevant.")

    typer.echo("\n[SUMMARY]")
    typer.echo(
        "Use 'rgd plugins list' to see live status, "
        "'rgd plugins allow <name>' to trust a plugin, "
        "and 'rgd plugins block <name>' to forbid it."
    )
    typer.echo("")


def attach(root: typer.Typer) -> None:
    """
    Attach this command group to the root CLI.

    Commands exposed:
        rgd plugins list
        rgd plugins allow <name>
        rgd plugins block <name>
        rgd plugins doctor
    """
    root.add_typer(app, name="plugins")
