# ZACMA Operations Dashboard

The dashboard is a local Next.js frontend for the FastAPI service in `../backend`.
It makes server-side requests to the backend, so no browser CORS configuration or credentials are needed for local development.

## Run locally

```powershell
cd dashboard
npm.cmd run dev -- -p 3001
```

Open `http://localhost:3001`. Port `3001` avoids the local Grafana service on port `3000`.

## Backend connection

Copy `.env.example` to `.env.local` only if the FastAPI server is not running at `http://127.0.0.1:8000`:

```text
API_BASE_URL=http://127.0.0.1:8000
```

The dashboard calls `/health`, `/api/v1/dashboard/overview`, and the existing module endpoints. The backend is queried only from the Next.js server. If tenant-scoped data is unavailable or the backend is offline, the UI labels its local sample values clearly and remains usable.

## Checks

```powershell
npm.cmd run lint
npm.cmd run build
```
