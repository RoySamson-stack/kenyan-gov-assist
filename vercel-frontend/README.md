# Serikali Yangu — Vercel Frontend

Next.js frontend for the Serikali Yangu Kenyan Government Assistant.

## Design

Features a Kenyan-themed UI with:
- Forest green and earth tone color palette
- Serikali Yangu (civic) and AfyaTranslate (healthcare) modes
- Sidebar with quick topics, PDF upload zone, and chat history
- Real-time chat with typing indicators
- Translation panel for AfyaTranslate mode
- Kenya flag stripe accent

## Deploy to Vercel

1. Push this folder to a GitHub repo
2. Go to [vercel.com](https://vercel.com) and import the repo
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your backend URL (e.g., `https://your-backend.railway.app`)
4. Deploy

## Local Development

```bash
cd vercel-frontend
npm install
npm run dev
```

## Backend Connection

Set `NEXT_PUBLIC_API_URL` to point to your backend API. Without it, chat requests will go to `/api/chat` which proxies to the backend.

The backend needs to be deployed separately. See the main project README for backend setup.
