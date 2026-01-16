# Twitter Lists RSS Converter

Convert public Twitter/X lists into RSS feeds.

## Features

- Add Twitter/X list URLs and generate RSS feeds
- Manage multiple lists with custom names
- Copy feed URLs for use in any RSS reader
- No Twitter API key required (uses web scraping via Nitter)
- Minimal, clean UI

## How It Works

This app scrapes Twitter lists through Nitter (a privacy-respecting Twitter frontend) and converts the tweets into standard RSS 2.0 feeds. No Twitter API access is required.

**Note**: Scraping reliability depends on Nitter instance availability. If feeds are empty, the Nitter instances may be temporarily unavailable.

## Deployment

### Railway

1. Create a new project on Railway
2. Deploy from this directory
3. Set environment variable `BASE_URL` to your Railway URL

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Visit `http://localhost:3000`

## Usage

1. Find a public Twitter list URL (e.g., `https://x.com/i/lists/123456789`)
2. Paste the URL in the input field
3. Optionally add a custom name
4. Click "Add"
5. Copy the generated RSS feed URL
6. Add to your RSS reader

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/lists` | GET | Get all lists |
| `/api/lists` | POST | Add a new list |
| `/api/lists/<id>` | PUT | Update a list |
| `/api/lists/<id>` | DELETE | Delete a list |
| `/feed/<id>` | GET | Get RSS feed |
| `/feed/<id>/preview` | GET | Preview tweets (JSON) |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `BASE_URL` | Public URL for feed links | http://localhost:3000 |
| `DEBUG` | Enable debug mode | false |

## Limitations

- Only works with **public** Twitter lists
- Tweet availability depends on Nitter instance uptime
- Rate limiting may affect large lists
- Media (images/videos) may not always load
