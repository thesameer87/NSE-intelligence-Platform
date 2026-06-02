# Render Deployment Guide

Deploying the NSE Intelligence Platform to Render requires creating two separate services:
1. A **Web Service** for the FastAPI Python Backend.
2. A **Static Site** for the React Frontend.

---

## 1. Deploy the Backend (FastAPI)

1. Go to your [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
2. Select **"Build and deploy from a Git repository"** and connect your `NSE-intelligence-Platform` repository.
3. Configure the service with the following settings:
   - **Name**: `nse-backend` (or similar)
   - **Root Directory**: `.` (leave empty or just use the root)
   - **Environment**: `Python`
   - **Region**: Select a region closest to your Supabase database (e.g., Singapore for AP-South)
   - **Branch**: `main`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Expand the **Advanced** section and click **Add Environment Variable**. Add all the secrets from your local `.env` file:
   - `ENVIRONMENT`: `production`
   - `SCHEDULER_INTERVAL_SECONDS`: `5`
   - `ANGEL_ONE_API_KEY`: *Your Key*
   - `ANGEL_ONE_CLIENT_ID`: *Your Client ID*
   - `ANGEL_ONE_PASSWORD`: *Your Password*
   - `SUPABASE_URL`: *Your Supabase URL*
   - `SUPABASE_KEY`: *Your Supabase Key*
   - `DATABASE_URL`: *Your Database URL*
   - `JWT_SECRET`: *Your JWT Secret*
   - `INTERNAL_API_TOKEN`: *Your Internal Token*
5. Click **Create Web Service**.
6. **Wait for the deployment to finish.** Once it is live, copy the public URL (e.g., `https://nse-backend.onrender.com`). You will need this for the frontend!

---

## 2. Deploy the Frontend (React / Vite)

1. Go back to the [Render Dashboard](https://dashboard.render.com/) and click **New > Static Site**.
2. Connect the exact same `NSE-intelligence-Platform` repository.
3. Configure the site with the following settings:
   - **Name**: `nse-dashboard` (or similar)
   - **Root Directory**: `frontend`  *(This is critical!)*
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `dist`
4. Expand the **Advanced** section and click **Add Environment Variable**:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: *Paste the backend URL you copied earlier (e.g., `https://nse-backend.onrender.com` without a trailing slash).*
5. Click **Create Static Site**.

### Fix Frontend Routing (Important for React SPA)
Because React uses client-side routing, you need to tell Render to redirect all paths to `index.html`.
1. Go to the settings page of your newly created **Static Site** (`nse-dashboard`).
2. Scroll down to the **Redirects/Rewrites** section.
3. Add a new rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
4. Click **Save Changes**.

---

## 3. Post-Deployment Checks

1. Visit your frontend URL provided by Render.
2. Check the browser console (F12) to ensure it is successfully connecting to your backend REST API and WebSocket streams.
3. Verify that your backend logs on Render show the `MockIngestionTask` (or real client) successfully inserting ticks into your database.
