#!/usr/bin/env python3
"""
MCP-Server für Meta Graph API (Marketing & Lead Generation)
Startet als STDIO-Server für Claude Code / Desktop.

Benötigt:
  pip install fastmcp requests python-dotenv
  META_ACCESS_TOKEN in .env oder als Umgebungsvariable setzen
"""

import os
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import requests

# -----------------------------------------------------------------------------
# Grund-Setup
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logging.info("Launching Meta Graph MCP…")

load_dotenv()  # liest META_ACCESS_TOKEN aus .env
mcp = FastMCP("MetaGraph")

# -----------------------------------------------------------------------------
# Meta Graph API Client
# -----------------------------------------------------------------------------
def _client():
    """Erzeugt Session mit Meta Graph API Credentials"""
    access_token = os.getenv("META_ACCESS_TOKEN")
    api_version = os.getenv("META_API_VERSION", "v23.0")

    if not access_token:
        raise RuntimeError("META_ACCESS_TOKEN not set")

    base_url = f"https://graph.facebook.com/{api_version}"

    session = requests.Session()
    session.params = {"access_token": access_token}

    return session, base_url


def _ad_account_id():
    """Gibt die konfigurierte Ad Account ID zurück"""
    account_id = os.getenv("META_AD_ACCOUNT_ID")
    if not account_id:
        raise RuntimeError("META_AD_ACCOUNT_ID not set")
    return account_id


# -----------------------------------------------------------------------------
# Tools
# -----------------------------------------------------------------------------
@mcp.tool()
def meta_me() -> str:
    """Schneller Check, ob das Token funktioniert (gibt User oder Page-Kontext zurück)."""
    session, base_url = _client()
    resp = session.get(f"{base_url}/me")
    return resp.text


@mcp.tool()
def marketing_create_campaign(
    name: str,
    objective: str,
    status: str = "PAUSED"
) -> str:
    """
    Lege eine Kampagne im Werbekonto an.
    objective z.B.: 'LEAD_GENERATION', 'AWARENESS', 'TRAFFIC', 'ENGAGEMENT', 'SALES' (je nach Version).
    status standardmäßig 'PAUSED', um sicher zu starten.
    """
    session, base_url = _client()
    ad_account_id = _ad_account_id()

    url = f"{base_url}/{ad_account_id}/campaigns"
    data = {
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": []  # Leer, falls keine Kategorien (z.B. Housing, Credit)
    }

    resp = session.post(url, json=data)
    result = resp.json()

    logging.info(f"Campaign created: {result}")
    return str(result)


@mcp.tool()
def marketing_upload_image_from_url(image_url: str) -> str:
    """
    Lade ein Bild hoch und erhalte image_hash, um es später in Ad Creatives zu verwenden.
    """
    session, base_url = _client()
    ad_account_id = _ad_account_id()

    url = f"{base_url}/{ad_account_id}/adimages"
    data = {"url": image_url}

    resp = session.post(url, json=data)
    result = resp.json()

    logging.info(f"Image upload response: {result}")

    # Extrahiere Hash aus der Response
    images = result.get("images", {})
    for key, value in images.items():
        image_hash = value.get("hash")
        if image_hash:
            return image_hash

    return str(result)


@mcp.tool()
def marketing_create_ad(
    name: str,
    adset_id: str,
    creative_id: str,
    status: str = "PAUSED"
) -> str:
    """
    Erstelle eine Ad (Anzeige) im Werbekonto.

    Args:
        name: Name der Anzeige
        adset_id: ID des Ad Sets (muss existieren)
        creative_id: ID des Ad Creative (muss existieren)
        status: Status (PAUSED oder ACTIVE)
    """
    session, base_url = _client()
    ad_account_id = _ad_account_id()

    url = f"{base_url}/{ad_account_id}/ads"
    data = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status
    }

    resp = session.post(url, json=data)
    result = resp.json()

    logging.info(f"Ad created: {result}")
    return str(result)


@mcp.tool()
def leads_create_instant_form(
    name: str,
    privacy_policy_url: str,
    page_id: str = None,
    questions_json: str = None,
    follow_up_url: str = None,
    thank_you_text: str = "Danke! Wir melden uns in Kürze.",
    locale: str = "de_DE",
    button_type: str = "VIEW_WEBSITE"
) -> str:
    """
    Erstelle eine Instant Lead Form (Leadgen-Formular) auf einer Page.
    - questions_json: JSON-String mit Fragen. Beispiel siehe unten.
    - button_type: VIEW_WEBSITE | CALL_BUSINESS | DOWNLOAD | SCHEDULE_APPOINTMENT | NONE | ...

    Beispiel für questions_json:
    [
      {"type": "FULL_NAME"},
      {"type": "EMAIL"},
      {"type": "PHONE"},
      {"type": "CUSTOM", "label": "Ihre Nachricht", "key": "message"}
    ]
    """
    session, base_url = _client()

    # Falls keine page_id mitgegeben, nutze die aus der .env
    if not page_id:
        page_id = os.getenv("META_PAGE_ID")
        if not page_id:
            raise RuntimeError("META_PAGE_ID not set and page_id not provided")

    url = f"{base_url}/{page_id}/leadgen_forms"

    # Standard-Fragen falls keine angegeben
    if not questions_json:
        questions_json = '[{"type": "FULL_NAME"}, {"type": "EMAIL"}, {"type": "PHONE"}]'

    data = {
        "name": name,
        "privacy_policy": {"url": privacy_policy_url},
        "questions": questions_json,
        "thank_you_page": {
            "title": "Vielen Dank!",
            "body": thank_you_text
        },
        "locale": locale
    }

    if follow_up_url:
        data["thank_you_page"]["button_type"] = button_type
        data["thank_you_page"]["button_text"] = "Weiter"
        data["thank_you_page"]["website_url"] = follow_up_url

    resp = session.post(url, json=data)
    result = resp.json()

    logging.info(f"Lead form created: {result}")
    return str(result)


@mcp.tool()
def marketing_get_leads(
    form_id: str,
    limit: int = 100
) -> str:
    """
    Rufe Leads aus einer Lead Form ab.

    Args:
        form_id: ID der Lead Form
        limit: Maximale Anzahl Leads (default: 100)
    """
    session, base_url = _client()

    url = f"{base_url}/{form_id}/leads"
    params = {"limit": limit}

    resp = session.get(url, params=params)
    result = resp.json()

    logging.info(f"Fetched {len(result.get('data', []))} leads")
    return str(result)


# -----------------------------------------------------------------------------
# Start MCP Server
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
