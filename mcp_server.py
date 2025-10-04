#!/usr/bin/env python3
"""
MCP-Server für Pandoc (Dokumentkonvertierung)
Startet als STDIO-Server für Claude Code / Desktop.

Benötigt:
  pip install fastmcp pypandoc python-dotenv
  pandoc muss installiert sein (brew install pandoc oder apt install pandoc)
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import pypandoc

# -----------------------------------------------------------------------------
# Grund-Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logging.info("Launching Pandoc MCP…")

load_dotenv()
mcp = FastMCP("Pandoc")

# -----------------------------------------------------------------------------
# Tools
# -----------------------------------------------------------------------------
@mcp.tool()
def convert_html_to_docx(
    input_html: str,
    output_path: str,
    header_text: str = None,
    footer_text: str = None,
    reference_doc: str = None
) -> str:
    """
    Konvertiert HTML zu Word (DOCX) mit optionalen Header/Footer.

    Args:
        input_html: HTML-String oder Pfad zur HTML-Datei
        output_path: Pfad für die Ausgabe-DOCX-Datei
        header_text: Optionaler Header-Text
        footer_text: Optionaler Footer-Text
        reference_doc: Pfad zu einer Referenz-DOCX-Datei für Styling

    Returns:
        Bestätigung mit Dateipfad
    """
    extra_args = []

    # Header und Footer als Metadaten hinzufügen
    if header_text:
        extra_args.extend(['--metadata', f'header-includes={header_text}'])

    if footer_text:
        extra_args.extend(['--metadata', f'footer-includes={footer_text}'])

    # Referenz-Dokument für Styling
    if reference_doc and os.path.exists(reference_doc):
        extra_args.extend(['--reference-doc', reference_doc])

    # Prüfen ob input_html ein Dateipfad ist
    if os.path.isfile(input_html):
        output = pypandoc.convert_file(
            input_html,
            'docx',
            outputfile=output_path,
            extra_args=extra_args
        )
    else:
        # Als HTML-String behandeln
        output = pypandoc.convert_text(
            input_html,
            'docx',
            format='html',
            outputfile=output_path,
            extra_args=extra_args
        )

    logging.info(f"Converted HTML to DOCX: {output_path}")
    return f"Erfolgreich konvertiert nach: {output_path}"


@mcp.tool()
def convert_html_to_docx_with_template(
    input_html: str,
    output_path: str,
    template_path: str
) -> str:
    """
    Konvertiert HTML zu Word (DOCX) mit einem Template.
    Das Template definiert Header, Footer und Styling.

    Args:
        input_html: HTML-String oder Pfad zur HTML-Datei
        output_path: Pfad für die Ausgabe-DOCX-Datei
        template_path: Pfad zur Template-DOCX-Datei

    Returns:
        Bestätigung mit Dateipfad
    """
    if not os.path.exists(template_path):
        return f"Fehler: Template nicht gefunden: {template_path}"

    extra_args = ['--reference-doc', template_path]

    # Prüfen ob input_html ein Dateipfad ist
    if os.path.isfile(input_html):
        output = pypandoc.convert_file(
            input_html,
            'docx',
            outputfile=output_path,
            extra_args=extra_args
        )
    else:
        # Als HTML-String behandeln
        output = pypandoc.convert_text(
            input_html,
            'docx',
            format='html',
            outputfile=output_path,
            extra_args=extra_args
        )

    logging.info(f"Converted HTML to DOCX with template: {output_path}")
    return f"Erfolgreich konvertiert mit Template nach: {output_path}"


@mcp.tool()
def create_docx_with_lua_filter(
    input_html: str,
    output_path: str,
    lua_filter_path: str,
    header_text: str = None,
    footer_text: str = None
) -> str:
    """
    Konvertiert HTML zu Word (DOCX) mit Lua-Filter für erweiterte Header/Footer-Kontrolle.

    Args:
        input_html: HTML-String oder Pfad zur HTML-Datei
        output_path: Pfad für die Ausgabe-DOCX-Datei
        lua_filter_path: Pfad zum Lua-Filter für Header/Footer
        header_text: Optionaler Header-Text (wird an Filter übergeben)
        footer_text: Optionaler Footer-Text (wird an Filter übergeben)

    Returns:
        Bestätigung mit Dateipfad
    """
    if not os.path.exists(lua_filter_path):
        return f"Fehler: Lua-Filter nicht gefunden: {lua_filter_path}"

    extra_args = ['--lua-filter', lua_filter_path]

    # Header/Footer als Variablen übergeben
    if header_text:
        extra_args.extend(['--variable', f'header={header_text}'])

    if footer_text:
        extra_args.extend(['--variable', f'footer={footer_text}'])

    # Prüfen ob input_html ein Dateipfad ist
    if os.path.isfile(input_html):
        output = pypandoc.convert_file(
            input_html,
            'docx',
            outputfile=output_path,
            extra_args=extra_args
        )
    else:
        # Als HTML-String behandeln
        output = pypandoc.convert_text(
            input_html,
            'docx',
            format='html',
            outputfile=output_path,
            extra_args=extra_args
        )

    logging.info(f"Converted HTML to DOCX with Lua filter: {output_path}")
    return f"Erfolgreich konvertiert mit Lua-Filter nach: {output_path}"


@mcp.tool()
def check_pandoc_version() -> str:
    """
    Prüft ob Pandoc installiert ist und gibt die Version zurück.

    Returns:
        Pandoc-Version
    """
    version = pypandoc.get_pandoc_version()
    logging.info(f"Pandoc version: {version}")
    return f"Pandoc Version: {version}"


@mcp.tool()
def list_pandoc_formats() -> str:
    """
    Listet alle verfügbaren Pandoc-Eingabe- und Ausgabeformate.

    Returns:
        Dictionary mit Input/Output-Formaten
    """
    formats = pypandoc.get_pandoc_formats()
    logging.info(f"Pandoc formats: {formats}")
    return str(formats)


# -----------------------------------------------------------------------------
# Start MCP Server
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
