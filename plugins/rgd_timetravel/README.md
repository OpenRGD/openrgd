# rgd-timetravel (Example Plugin)

This is an example external plugin for the OpenRGD ecosystem.

It demonstrates how to:

- expose a new command group under `rgd timetravel`
- declare an entry point in the `rgd.commands` group
- build a simple "time-travel" interface for the Cognitive BIOS

## Install (development)

From this directory:

pip install -e .

Then:

Copia codice
rgd plugins list
rgd timetravel --help
You should see the new commands registered.

python
Copia codice

---

### `plugins/rgd-timetravel/src/rgd_timetravel/__init__.py`

"""
rgd-timetravel

Example external plugin for OpenRGD that adds a "timetravel" command group.
"""

__all__ = ["cli"]