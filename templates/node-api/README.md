# Node.js API Template for Railway

A production-ready Express.js API template configured for Railway deployment.

## Features

- Express.js web framework
- CORS enabled
- Environment variable support
- Health check endpoint
- Error handling
- JSON request/response
- Production-ready configuration

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Run in development mode
npm run dev

# Run in production mode
npm start
```

The API will be available at `http://localhost:3000`

### Deploy to Railway

#### Option 1: Via Dashboard
1. Push this folder to GitHub
2. Go to railway.app/dashboard
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Done! Railway auto-detects Node.js and deploys

#### Option 2: Via CLI
```bash
railway init
railway up
```

## Endpoints

- `GET /` - Welcome message with API info
- `GET /health` - Health check (returns status, timestamp, uptime)
- `GET /api` - Example API endpoint
- `POST /api/echo` - Echo back the request body

## Environment Variables

Railway automatically provides:
- `PORT` - The port your app should listen on
- `RAILWAY_ENVIRONMENT` - Current environment (production/staging)

Add your own in Railway dashboard or via CLI:
```bash
railway variables set API_KEY=your-secret-key
```

## Adding a Database

### PostgreSQL
```bash
# Via CLI
railway add postgresql

# Then use in your code:
const DATABASE_URL = process.env.DATABASE_URL;
```

### Redis
```bash
railway add redis
# Access via: process.env.REDIS_URL
```

## Customizing

1. Edit `index.js` to add your endpoints
2. Add dependencies: `npm install package-name`
3. Update `package.json` scripts as needed
4. Set environment variables in Railway

## Testing

```bash
# Test health endpoint
curl http://localhost:3000/health

# Test API endpoint
curl http://localhost:3000/api

# Test POST endpoint
curl -X POST http://localhost:3000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Production Checklist

- [ ] Environment variables set in Railway
- [ ] Secrets not committed to git
- [ ] Health check endpoint working
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Database connections tested (if using)

## Troubleshooting

**App won't start on Railway:**
- Check logs: `railway logs`
- Ensure `PORT` environment variable is used (Railway provides this)
- Verify `start` script in package.json

**502 Bad Gateway:**
- App must listen on `0.0.0.0`, not `localhost`
- App must use `process.env.PORT`

**Can't connect to database:**
- Check `railway variables` for DATABASE_URL
- Ensure database service is running in Railway dashboard
