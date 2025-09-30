#!/usr/bin/env python3
"""
MCP-Server für Google Gemini API (Veo-Video & Imagen-Bilder)
Startet als STDIO-Server für Claude Code / Desktop.

Benötigt:
  pip install modelcontextprotocol[server] fastmcp google-genai python-dotenv
  GOOGLE_API_KEY in .env oder als Umgebungsvariable setzen
"""

import os
import base64
import time
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# -----------------------------------------------------------------------------
# Grund-Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logging.info("Launching MCP…")

load_dotenv()  # liest GOOGLE_API_KEY aus .env
mcp = FastMCP("veo")

# Ausgabeverzeichnis für generierte Dateien
OUTPUT_DIR = Path("generated_files")
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Google Gemini API Client
# -----------------------------------------------------------------------------
from google import genai
from google.genai import types


def _client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    return genai.Client(api_key=api_key)


# -----------------------------------------------------------------------------
# Tools
# -----------------------------------------------------------------------------
@mcp.tool()
def healthcheck() -> str:
    """Einfacher Server-Check."""
    return "ok"


@mcp.tool()
def generate_image(
    prompt: str,
    model: str = "imagen-4.0-generate-001",
    output_path: str = None,
) -> str:
    """
    Erzeugt ein Social-Media-Bild via Google Imagen.
    Rückgabe: Dateipfad zum gespeicherten Bild.

    Args:
        prompt: Beschreibung des zu generierenden Bildes
        model: Modell-ID (Standard: imagen-4.0-generate-001)
        output_path: Optional - vollständiger Dateipfad oder Verzeichnis zum Speichern
    """
    client = _client()
    resp = client.models.generate_images(model=model, prompt=prompt)

    if not resp.generated_images:
        raise RuntimeError("No images generated")

    img = resp.generated_images[0].image
    data = getattr(img, "image_bytes", None) or getattr(img, "bytes", None)
    if not data:
        raise RuntimeError("No image bytes in response")

    # Zielpfad bestimmen
    if output_path:
        filepath = Path(output_path)
        if filepath.is_dir():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            filepath = filepath / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        filepath = OUTPUT_DIR / filename

    # Bild speichern
    filepath.write_bytes(data)
    logging.info("Image saved to: %s", filepath)

    return str(filepath.absolute())


@mcp.tool()
def generate_video(
    prompt: str,
    model: str = "veo-3.0-generate-001",  # Alternativ: veo-3.0-fast-generate-001
    aspect_ratio: str = None,             # z.B. "9:16" für Reels
    resolution: str = None,               # "720p" oder "1080p"
    output_path: str = None,
    poll_interval: int = 5,
) -> str:
    """
    Erzeugt ein kurzes Video via Google Veo 3.
    Rückgabe: Dateipfad zum gespeicherten Video.

    Args:
        prompt: Beschreibung des zu generierenden Videos
        model: Modell-ID (Standard: veo-3.0-generate-001)
        aspect_ratio: Optional - z.B. "9:16" für Reels
        resolution: Optional - "720p" oder "1080p"
        output_path: Optional - vollständiger Dateipfad oder Verzeichnis zum Speichern
        poll_interval: Polling-Intervall in Sekunden (Standard: 5)
    """
    client = _client()

    cfg = None
    if aspect_ratio or resolution:
        cfg = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio if aspect_ratio else None,
            resolution=resolution if resolution else None,
        )

    op = client.models.generate_videos(model=model, prompt=prompt, config=cfg)
    logging.info("Video generation started: %s", op.name)

    # Polling, bis Operation fertig ist
    while not op.done:
        time.sleep(poll_interval)
        op = client.operations.get(op)
        logging.info("…waiting for video generation (%s)", op.name)

    if not op.response.generated_videos:
        raise RuntimeError("No video returned in operation response")

    gv = op.response.generated_videos[0]

    # Video herunterladen (füllt gv.video.video_bytes)
    client.files.download(file=gv.video)
    data = getattr(gv.video, "video_bytes", None) or getattr(gv.video, "bytes", None)
    if not data:
        raise RuntimeError("No video bytes received after download()")

    # Zielpfad bestimmen
    if output_path:
        filepath = Path(output_path)
        if filepath.is_dir():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            filepath = filepath / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.mp4"
        filepath = OUTPUT_DIR / filename

    # Video speichern
    filepath.write_bytes(data)
    logging.info("Video saved to: %s", filepath)

    return str(filepath.absolute())


# -----------------------------------------------------------------------------
# Start MCP Server
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()