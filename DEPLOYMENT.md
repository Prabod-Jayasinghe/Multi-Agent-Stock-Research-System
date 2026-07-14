# 🚀 Deployment Guide — Multi-Agent Stock Research System

This guide walks you through deploying the **Multi-Agent Stock Research System** to production using free-tier cloud services:
* **Backend (API)**: [Render.com](https://render.com/) (Web Service)
* **Frontend (UI)**: [Vercel](https://vercel.com/) (Static Web App)
* **Database (Optional)**: [Supabase](https://supabase.com/) (PostgreSQL)

---

## 💾 Step 1: Database Setup (Supabase)

*If you do not want to persist report history, you can skip this step. The backend will automatically fall back to an in-memory database store.*

1. Go to [Supabase](https://supabase.com/) and create a free account.
2. Click **New Project** and set up a PostgreSQL database.
3. Once the database is provisioned, go to **Project Settings** -> **Database**.
4. Copy the **URI Connection String** under "Connection string" (select the **Transaction** mode or standard mode, and make sure it looks like `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`).
5. Replace `[YOUR-PASSWORD]` with the database password you chose. Keep this URL handy.

---

## 🐍 Step 2: Deploy Backend to Render

1. Create a free account on [Render](https://render.com/) and connect your GitHub repository.
2. Click **New +** -> **Web Service**.
3. Select your repository.
4. Configure the Web Service settings:
   * **Name**: `stock-research-backend`
   * **Region**: Choose the closest region to your users.
   * **Branch**: `phase/8-polishing-and-cleanup` (or your main production branch)
   * **Root Directory**: `backend`
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python main.py` (or `uvicorn main:app --host 0.0.0.0 --port $PORT`)
   * **Instance Type**: `Free`
5. Click **Advanced** and add the following **Environment Variables**:
   * `GROQ_API_KEY`: Your real Groq API key (`gsk_...`)
   * `GROQ_MODEL`: `llama-3.1-8b-instant`
   * `GNEWS_API_KEY`: Your real GNews API key
   * `DATABASE_URL`: *Your Supabase Connection URI (leave blank to run in-memory)*
   * `BACKEND_PORT`: `10000` (Render's default port, or let Render override it via `$PORT`)
   * `CORS_ORIGINS`: `https://your-frontend-domain.vercel.app` *(update this after creating the Vercel frontend in Step 3)*
6. Click **Create Web Service**. Wait for the build and deployment to finish. Once done, copy the generated Render service URL (e.g. `https://stock-research-backend.onrender.com`).

---

## ⚛️ Step 3: Deploy Frontend to Vercel

1. Create a free account on [Vercel](https://vercel.com/) and connect your GitHub repository.
2. Click **Add New** -> **Project**.
3. Select your repository and click **Import**.
4. Configure the Project settings:
   * **Framework Preset**: `Vite` (Vercel will auto-detect this)
   * **Root Directory**: `frontend`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
5. Expand the **Environment Variables** section and add:
   * `VITE_API_URL`: *The Render Backend URL you copied in Step 2* (e.g. `https://stock-research-backend.onrender.com`)
6. Click **Deploy**. Vercel will build and host your frontend.
7. Once deployment succeeds, copy your Vercel URL (e.g., `https://your-project.vercel.app`).
8. **Crucial**: Go back to your Render Web Service dashboard, navigate to **Environment**, and update the `CORS_ORIGINS` variable with your new Vercel frontend URL. Save changes to trigger a clean redeploy of the backend.

---

## 🔎 Step 4: Verification

1. Visit your Vercel frontend URL in the browser.
2. Enter `TSLA` or `RELIANCE.NS` in the Search bar and click **Run Analysis**.
3. Open the browser's developer console (F12) to inspect the API requests. They should resolve instantly through the Render Web Service without any CORS blocks.
4. Run a PDF export to verify the layout formats correctly.
