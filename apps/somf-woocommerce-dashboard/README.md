# SOMF WooCommerce Dashboard

A KPI dashboard for State of Mind Fitness that displays membership and revenue metrics from WooCommerce.

## Features

- **Real-time KPIs**: Month-to-date revenue, prior month revenue, active members, pending cancellations, pending payments, on-hold members
- **Trend Charts**: Active members trend and prior month revenue trend with selectable time periods
- **Auto-refresh**: Data refreshes automatically every 5 minutes
- **Caching**: 5-minute cache to reduce WooCommerce API calls
- **Embeddable**: Separate `/embed` endpoint for Squarespace integration

## Deployment on Railway

### Environment Variables

Set these in your Railway service:

| Variable | Description |
|----------|-------------|
| `WC_URL` | Your WooCommerce store URL (e.g., `https://www.stateofmindfitness.com`) |
| `WC_CONSUMER_KEY` | WooCommerce REST API consumer key |
| `WC_CONSUMER_SECRET` | WooCommerce REST API consumer secret |
| `PORT` | Port to run on (Railway sets this automatically) |

### Deploy Steps

1. Create a new Railway project
2. Connect this repository
3. Set the root directory to `apps/somf-woocommerce-dashboard`
4. Add the environment variables above
5. Deploy!

## Squarespace Embed

To embed on Squarespace:

1. Go to your Squarespace page editor
2. Add a "Code" block
3. Paste this iframe code:

```html
<iframe
  src="https://YOUR-RAILWAY-APP-URL.railway.app/embed"
  width="100%"
  height="1000"
  frameborder="0"
  style="border: none; max-width: 500px; margin: 0 auto; display: block;">
</iframe>
```

Replace `YOUR-RAILWAY-APP-URL` with your actual Railway deployment URL.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/embed` | GET | Embeddable widget version |
| `/health` | GET | Health check |
| `/api/metrics` | GET | Current KPI metrics |
| `/api/historical-active-members?days=N` | GET | Historical member counts |
| `/api/historical-revenue?days=N` | GET | Historical revenue data |
| `/api/refresh` | POST | Force cache refresh |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your WooCommerce credentials

# Run the app
python app.py
```

Visit `http://localhost:5000` to see the dashboard.
# Deployment trigger: Sat Jan 17 08:49:31 UTC 2026
