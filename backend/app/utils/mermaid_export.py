from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import struct
import zlib


def _placeholder_svg(mermaid_text: str, output_path: str) -> str:
    escaped = (
        mermaid_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800">
  <rect width="100%" height="100%" fill="#f9fbff" />
  <text x="30" y="40" font-family="monospace" font-size="20" fill="#0f172a">Architecture Mermaid Source</text>
  <foreignObject x="20" y="60" width="1160" height="720">
    <pre xmlns="http://www.w3.org/1999/xhtml" style="font-family: monospace; font-size: 14px; color: #1f2937;">{escaped}</pre>
  </foreignObject>
</svg>'''
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    return str(path)


def _find_mmdc() -> str | None:
    # 1) Explicit env override.
    env_path = os.getenv("COPILOT_MERMAID_CLI_PATH", "").strip()
    if env_path and Path(env_path).exists():
        return env_path

    # 2) PATH lookup.
    from_path = shutil.which("mmdc")
    if from_path:
        return from_path

    # 3) Workspace-local fallback (backend + frontend sibling folders).
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "frontend" / "node_modules" / ".bin" / "mmdc",
        here.parents[2] / "frontend" / "node_modules" / ".bin" / "mmdc",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack("!I", len(data))
        + chunk_type
        + data
        + struct.pack("!I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def _placeholder_png(output_path: str, width: int = 1200, height: int = 800) -> str:
    # Valid fallback PNG (light blue background) so outputs are never zero bytes.
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = _png_chunk(
        b"IHDR",
        struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0),  # 8-bit RGB
    )

    row = b"\x00" + (b"\xEE\xF4\xFF" * width)  # filter byte + pixels
    raw = row * height
    compressed = zlib.compress(raw, level=9)
    idat = _png_chunk(b"IDAT", compressed)
    iend = _png_chunk(b"IEND", b"")

    path.write_bytes(signature + ihdr + idat + iend)
    return str(path)


def mermaid_to_svg(mermaid_text: str, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    mmdc = _find_mmdc()
    if not mmdc:
        return _placeholder_svg(mermaid_text, output_path)

    temp = out.with_suffix(".mmd")
    temp.write_text(mermaid_text, encoding="utf-8")
    cmd = [mmdc, "-i", str(temp), "-o", str(out), "-b", "transparent"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return str(out)
    except subprocess.CalledProcessError:
        return _placeholder_svg(mermaid_text, output_path)
    finally:
        if temp.exists():
            temp.unlink()


def mermaid_to_png(mermaid_text: str, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    mmdc = _find_mmdc()
    if not mmdc:
        return _placeholder_png(output_path)

    temp = out.with_suffix(".mmd")
    temp.write_text(mermaid_text, encoding="utf-8")
    cmd = [mmdc, "-i", str(temp), "-o", str(out), "-b", "transparent"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return str(out)
    except subprocess.CalledProcessError:
        return _placeholder_png(output_path)
    finally:
        if temp.exists():
            temp.unlink()
