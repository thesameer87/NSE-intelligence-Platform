# Vercel Deployment Guide (Frontend)

Vercel is the recommended platform for deploying the React (Vite) frontend due to its edge network and seamless developer experience.

## Step-by-Step Instructions

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
2. Connect your GitHub account and import the `NSE-intelligence-Platform` repository.
3. In the "Configure Project" screen, you **MUST** change the Root Directory:
   - **Root Directory**: Click "Edit" and select the `frontend` folder.
4. Leave the Framework Preset as `Vite` (Vercel usually auto-detects this). The Build and Output Settings should automatically fill with:
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Expand the **Environment Variables** section and add:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: *[Paste your Render Backend URL here, e.g., `https://nse-backend.onrender.com`]*
6. Click **Deploy**.

## Routing Configuration
A `vercel.json` file has already been added to the `frontend/` directory in the repository. This automatically tells Vercel to route all traffic to `index.html`, ensuring your React Single Page Application (SPA) routing works perfectly without throwing 404 errors when you refresh the page.
