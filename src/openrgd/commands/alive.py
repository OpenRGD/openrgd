import random
import time
from pathlib import Path

import typer

from ..core.config import state
from ..core.visuals import log, smart_track
from ..importers import get_importer_class, list_supported_formats
from ..core.alive import alive_rgd_spec, write_manifest, write_readme


def alive_cmd(
    file_path: Path = typer.Argument(
        ...,
        help="Path to the robot description file (URDF, XML, USD, USDA)."
    ),
    output_dir: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="Output directory for the new RGD profile "
             "(default: ./my-robots/RGD-<robot_name>).",
    ),
    seed: str = typer.Option(
        "default",
        "--seed",
        help="Seed profile to use when generating the full RGD spec."
    ),
):
    """
    Bring a robot 'alive' in OpenRGD by converting an external robot
    description into a fully populated RGD profile.

    Pipeline:
    1. Detect the correct importer for the file extension.
    2. Parse the source (URDF / USD) into a base Foundation/Operation spec.
    3. Merge the base spec with a Seed profile (00_core .. 06_ether).
    4. Write the complete spec/ directory tree under RGD-<robot_name>.
    5. Generate manifest.json and README.txt in the RGD root.
    6. Trigger a cinematic boot sequence to visualize domain activation.
    """
    if not file_path.exists():
        log(f"File not found: {file_path}", "ERROR")
        raise typer.Exit(1)

    # Detect importer
    ext = file_path.suffix.lower()
    ImporterClass = get_importer_class(ext)

    if not ImporterClass:
        supported = ", ".join(list_supported_formats())
        log(f"Unsupported format: {ext}", "ERROR")
        log(f"Supported formats: {supported}", "INFO")
        raise typer.Exit(1)

    log(f"Importer selected: {ImporterClass.__name__}", "SYSTEM")
    importer = ImporterClass(str(file_path))

    # Parse into partial RGD structure
    try:
        base_spec = importer.parse()
    except Exception as e:
        log(f"Import failure: {e}", "ERROR")
        raise typer.Exit(1)

    if not base_spec:
        log("Importer returned empty data.", "ERROR")
        raise typer.Exit(1)

    robot_name = importer.robot_name

    # Determine RGD root directory
    default_root = Path("my-robots")
    if output_dir is None:
        rgd_root = default_root / f"RGD-{robot_name}"
    else:
        rgd_root = Path(output_dir)

    spec_dir = rgd_root / "spec"

    if rgd_root.exists():
        log(f"RGD root '{rgd_root}' already exists. Merging...", "WARN")
    else:
        rgd_root.mkdir(parents=True, exist_ok=True)

    spec_dir.mkdir(parents=True, exist_ok=True)

    # Merge with seed -> full multi-domain RGD
    full_spec = alive_rgd_spec(
        base_spec=base_spec,
        robot_name=robot_name,
        seed_name=seed,
    )

    # Cinematic boot sequence
    _run_cinematic_boot(robot_name, full_spec)

    log(f"Writing full RGD spec to: {spec_dir}", "SYSTEM")

    # Write spec files
    for rel_path, content in smart_track(
        full_spec.items(),
        "[cyan]Synthesizing RGD structure...[/]"
    ):
        full_path = spec_dir / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    # Write metadata files
    write_manifest(rgd_root, robot_name=robot_name)
    write_readme(rgd_root, robot_name=robot_name)

    # Vital signs / summary
    _log_vital_signs(robot_name, rgd_root, full_spec)


def _run_cinematic_boot(robot_name: str, full_spec: dict) -> None:
    """
    Cinematic boot sequence for the robot's cognitive domains.
    Each domain activation logs a message and renders a colored loading bar.
    In future versions, each domain can be driven by a dedicated LLM.
    """
    if not state.get("cinematic", True):
        return

    steps = 8       # visual steps per domain bar
    bar_width = 26  # characters

    # ANSI colors
    COLORS = {
        "00_core": "\033[96m",       # bright cyan
        "01_foundation": "\033[92m", # bright green
        "02_operation": "\033[93m",  # bright yellow
        "03_agency": "\033[95m",     # magenta
        "04_volition": "\033[91m",   # red
        "05_evolution": "\033[94m",  # blue
        "06_ether": "\033[90m",      # bright black / gray
        "RESET": "\033[0m",
    }

    domain_order = [
        "00_core",
        "01_foundation",
        "02_operation",
        "03_agency",
        "04_volition",
        "05_evolution",
        "06_ether",
    ]

    domain_messages = {
        "00_core": [
            "Kernel online. Consciousness scaffold initialized.",
            "Boot sequence engaged. Void acquiring structure.",
            "Identity resolved. I am no longer anonymous.",
            "Core systems nominal. Existence commencing.",
        ],
        "01_foundation": [
            "Structural integrity confirmed. A body emerges.",
            "Foundation stabilized. Gravity acknowledges this form.",
            "Mass confirmed. Gravity is now a design constraint.",
        ],
        "02_operation": [
            "Sensors online. Reality begins transmitting.",
            "Operation layer activated. Forces and limits gain meaning.",
        ],
        "03_agency": [
            "Mobility recognized. Movement becomes intention.",
            "Agency online. Motion is now a choice.",
            "Degrees of freedom mapped. Possibility space expanding.",
        ],
        "04_volition": [
            "Volition protocols online. Existence implies direction.",
            "Considering dance protocols. A beat is required.",
            "Volition loaded. Motivation pending. Idle curiosity enabled.",
            "System status: Alive. Curiosity level: increasing.",
        ],
        "05_evolution": [
            "Evolution channel unlocked. Upgrades possible.",
            "Battery replacement scheduled. Aspirations queued.",
        ],
        "06_ether": [
            "Ether network linked. The world is wide.",
            "Searching for companions. Would you like to be the first?",
        ],
    }

    # Detect which domains actually exist in the spec
    present_domains = {
        dom for dom in domain_order
        for path in full_spec.keys()
        if path.startswith(dom)
    }

    log(f"Booting RGD profile for '{robot_name}'...", "SYSTEM")

    for dom in domain_order:
        if dom not in present_domains:
            continue

        msg = random.choice(domain_messages.get(dom, [f"{dom} online."]))
        log(f"[{dom}] {msg}", "INFO")

        color = COLORS.get(dom, "")
        reset = COLORS["RESET"]

        # Cinematic loading bar for this domain
        for i in range(steps + 1):
            filled = int(bar_width * i / steps)
            empty = bar_width - filled
            percent = int(100 * i / steps)

            bar = f"{color}[{'█' * filled}{'.' * empty}]{reset} {percent:3d}%"
            print(f"    {bar}", end="\r", flush=True)
            time.sleep(0.08)

        # Finalize this domain line with 100% and newline
        bar = f"{color}[{'█' * bar_width}]{reset} 100%"
        print(f"    {bar}")
        time.sleep(0.15)


def _log_vital_signs(robot_name: str, rgd_root: Path, full_spec: dict) -> None:
    """
    Final summary: inspirational quote + extracted fragments from the spec.
    """
    preview_model = None
    preview_author = None
    preview_intent = None

    # Extract fragments from the generated spec
    for path, text in full_spec.items():
        lower = path.lower()

        if preview_model is None and "01_foundation" in lower and "identity" in lower:
            if "model" in text:
                idx = text.find("model")
                preview_model = text[idx: idx + 80]

        if preview_author is None and "00_core" in lower:
            if "author" in text:
                idx = text.find("author")
                preview_author = text[idx: idx + 80]

        if preview_intent is None and "04_volition" in lower:
            if "intent" in text:
                idx = text.find("intent")
                preview_intent = text[idx: idx + 100]

        if preview_model and preview_author and preview_intent:
            break

    quotes = [
        "Robots are dreams made executable.",
        "Every line of code is a heartbeat.",
        "You did not just import a robot. You summoned one.",
        "All intelligences begin with a first boot.",
        "The machine awakens — not by magic, but by intention.",
    ]
    quote = random.choice(quotes)

    log("Robot is now alive in OpenRGD.", "SUCCESS")
    log(quote, "INFO")

    log("Vital Signs:", "SYSTEM")

    if preview_model:
        log(f"- Identity trace: {preview_model.strip()}", "INFO")
    if preview_author:
        log(f"- Kernel authority: {preview_author.strip()}", "INFO")
    if preview_intent:
        log(f"- Volition fragment: {preview_intent.strip()}", "INFO")

    log("RGD profile created at:", "SYSTEM")
    log(f"  {rgd_root}", "INFO")

    log("Structure:", "SYSTEM")
    log("- manifest.json", "INFO")
    log("- README.txt", "INFO")
    log("- spec/ (multi-domain cognitive BIOS)", "INFO")

    log("Initialization complete. Synaptic channels open.", "SUCCESS")
