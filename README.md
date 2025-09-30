# Meta Graph API MCP Server

Python MCP Server for Meta Graph API integration with critical marketing endpoints.

## Features

- ✅ Campaign creation and management
- ✅ Image upload for ad creatives
- ✅ Ad creation
- ✅ Lead generation form creation
- ✅ Lead data retrieval
- ✅ Simple, single-file implementation
- ✅ FastMCP-based architecture

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Meta credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
META_ACCESS_TOKEN=your_meta_access_token_here
META_AD_ACCOUNT_ID=act_123456789
META_API_VERSION=v23.0
META_PAGE_ID=123456789  # Optional, for lead forms
```

### Getting Meta Credentials

1. **Access Token**: Get from [Meta for Developers](https://developers.facebook.com/tools/explorer)
   - Select your app
   - Generate token with permissions: `ads_management`, `leads_retrieval`, `pages_read_engagement`

2. **Ad Account ID**: Find in [Ads Manager](https://business.facebook.com/adsmanager)
   - Format: `act_123456789`

3. **Page ID**: Find in Page settings or use Graph API Explorer

## Usage

### Run as MCP Server

```bash
python meta_mcp_server.py
```

### Available Tools

#### 1. `meta_me`
Quick token validation - returns user/page context.

```python
meta_me()
```

#### 2. `marketing_create_campaign`
Create a new ad campaign.

```python
marketing_create_campaign(
    name="Summer Campaign 2025",
    objective="LEAD_GENERATION",  # or TRAFFIC, AWARENESS, SALES, etc.
    status="PAUSED"  # Start paused for safety
)
```

#### 3. `marketing_upload_image_from_url`
Upload image from URL, returns hash for use in creatives.

```python
marketing_upload_image_from_url(
    image_url="https://example.com/image.jpg"
)
# Returns: "02bee5277ec507b6fd0f9b9ff2f22d9c"
```

#### 4. `marketing_create_ad`
Create an ad (requires existing adset_id and creative_id).

```python
marketing_create_ad(
    name="Summer Promo Ad",
    adset_id="123456789",
    creative_id="987654321",
    status="PAUSED"
)
```

#### 5. `leads_create_instant_form`
Create a lead generation form.

```python
leads_create_instant_form(
    name="Contact Form",
    privacy_policy_url="https://example.com/privacy",
    page_id="123456789",  # Optional if set in .env
    questions_json='[{"type":"FULL_NAME"},{"type":"EMAIL"},{"type":"PHONE"}]',
    follow_up_url="https://example.com/thank-you",
    thank_you_text="Vielen Dank für Ihr Interesse!",
    locale="de_DE",
    button_type="VIEW_WEBSITE"
)
```

**Question Types**:
- `FULL_NAME`, `EMAIL`, `PHONE`, `DATE_OF_BIRTH`
- `GENDER`, `ZIP_CODE`, `CITY`, `STATE`
- `CUSTOM` (with `label` and `key` fields)

#### 6. `marketing_get_leads`
Retrieve leads from a form.

```python
marketing_get_leads(
    form_id="123456789",
    limit=100
)
```

## Integration with Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "meta-graph": {
      "command": "python",
      "args": ["/Users/benedikt.hoheisel/mcp/meta-graph/meta_mcp_server.py"],
      "env": {
        "META_ACCESS_TOKEN": "your_token",
        "META_AD_ACCOUNT_ID": "act_123456789",
        "META_API_VERSION": "v23.0"
      }
    }
  }
}
```

Or use STDIO mode:

```json
{
  "mcpServers": {
    "meta-graph": {
      "type": "stdio",
      "command": "python",
      "args": ["/Users/benedikt.hoheisel/mcp/meta-graph/meta_mcp_server.py"]
    }
  }
}
```

## API Version

Current: **v23.0** (January 2025)

Update `META_API_VERSION` in `.env` to use a different version.

## Common Objectives

- `OUTCOME_LEADS` - Lead generation
- `OUTCOME_TRAFFIC` - Drive traffic to website/app
- `OUTCOME_AWARENESS` - Increase brand awareness
- `OUTCOME_SALES` - Drive sales/conversions
- `OUTCOME_ENGAGEMENT` - Increase engagement
- `OUTCOME_APP_PROMOTION` - Promote mobile app

## Error Handling

Per the coding style guide, this implementation uses simple, direct API calls without try/except blocks. Check API responses for error objects:

```python
{
  "error": {
    "message": "Invalid OAuth access token",
    "type": "OAuthException",
    "code": 190
  }
}
```

## Resources

- [Meta Marketing API Docs](https://developers.facebook.com/docs/marketing-api)
- [Graph API Reference](https://developers.facebook.com/docs/graph-api/reference)
- [Meta Business Help Center](https://www.facebook.com/business/help)
- [API Changelog](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog)

## License

MIT
