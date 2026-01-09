# Next.js App Template for Railway

A production-ready Next.js template configured for Railway deployment.

## Features

- Next.js 14 with App Router
- TypeScript support
- Production-ready configuration
- API routes included
- Automatic Railway deployment

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Deploy to Railway

#### Option 1: Via Dashboard
1. Push this folder to GitHub
2. Go to railway.app/dashboard
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Done! Railway auto-detects Next.js and deploys

#### Option 2: Via CLI
```bash
railway init
railway up
```

## Project Structure

```
nextjs-app/
├── app/
│   ├── page.tsx          # Home page
│   ├── layout.tsx        # Root layout
│   └── api/              # API routes
│       └── health/
│           └── route.ts  # Health check endpoint
├── public/               # Static files
└── package.json
```

## Environment Variables

Set in Railway dashboard or via CLI:
```bash
railway variables set NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

Note: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## API Routes

Built-in API routes:
- `GET /api/health` - Health check endpoint

Add more in `app/api/` directory.

## Building for Production

Railway automatically runs:
```bash
npm run build
npm start
```

## Troubleshooting

**Build fails:**
- Check logs: `railway logs`
- Ensure all dependencies in package.json
- Verify Node version compatibility

**Environment variables not working:**
- Browser variables must start with `NEXT_PUBLIC_`
- Server-only variables don't need prefix
