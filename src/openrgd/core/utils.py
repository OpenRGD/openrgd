import json
from pathlib import Path
import typer
from rich.panel import Panel
from .config import console
from .visuals import log

def find_default_kernel() -> Path:
    """
    Looks for the kernel in standard locations relative to CWD or Project Root.
    Target: spec/00_core/kernel.jsonc
    """
    current_dir = Path.cwd()
    
    candidates = [
        # 1. Standard Structure (Root/spec/00_core/kernel.jsonc)
        current_dir / "spec" / "00_core" / "kernel.jsonc",
        
        # 2. Inside Spec (Root/spec/kernel.jsonc - sometimes used)
        current_dir / "spec" / "kernel.jsonc",
        
        # 3. Direct (If you are inside 00_core)
        current_dir / "kernel.jsonc",
        
        # 4. Legacy/Dev (Root/00_core/kernel.jsonc)
        current_dir / "00_core" / "kernel.jsonc",
    ]
    
    for c in candidates:
        if c.exists():
            return c.resolve()
            
    return None

def strip_jsonc(text: str) -> str:
    """Robust JSONC stripper (Character-based)."""
    output = []
    i = 0
    length = len(text)
    in_string = False
    in_comment_line = False
    in_comment_block = False
    
    while i < length:
        char = text[i]
        next_char = text[i+1] if i + 1 < length else ''
        
        if char == '"' and not in_comment_line and not in_comment_block:
            if i > 0 and text[i-1] == '\\' and not (i > 1 and text[i-2] == '\\'): pass
            else: in_string = not in_string
            output.append(char); i += 1; continue
        if in_string:
            output.append(char); i += 1; continue
        if not in_comment_line and not in_comment_block:
            if char == '/' and next_char == '/': in_comment_line = True; i += 2; continue
            if char == '/' and next_char == '*': in_comment_block = True; i += 2; continue
        if in_comment_line and char == '\n':
            in_comment_line = False; output.append(char); i += 1; continue
        if in_comment_block and char == '*' and next_char == '/':
            in_comment_block = False; i += 2; continue
        if not in_comment_line and not in_comment_block:
            output.append(char)
        i += 1
    return "".join(output)

def load_jsonc(path: Path) -> dict:
    if not path.exists():
        log(f"File not found: {path}", "ERROR")
        raise FileNotFoundError(f"Missing module: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    try:
        return json.loads(strip_jsonc(raw), strict=False)
    except json.JSONDecodeError as e:
        log(f"Syntax Error in: {path.name}", "ERROR")
        console.print(f"[red]JSON Error at line {e.lineno}: {e.msg}[/]")
        raise typer.Exit(1)