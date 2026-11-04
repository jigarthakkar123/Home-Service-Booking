# Production Deployment Guide

This guide walks you through deploying the **HomeServe Technologies SaaS Platform** using **Render** for the FastAPI backend and **Netlify** for the React frontend.

---

## 1. Version Control & GitHub Repository Setup

### Step 1: Initialize & Commit (Already initialized locally)
```bash
git add .
git commit -m "feat: complete Full Stack Capstone Home Services Booking SaaS Platform"
```

### Step 2: Push to GitHub
1. Create a new repository on your GitHub account (e.g. `homeserve-saas`).
2. Push your local repository:
```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/homeserve-saas.git
git branch -M main
git push -u origin main
```

---

## 2. Deploying Backend to Render

1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `homeserve-saas`.
4. Configure service details:
   - **Name**: `homeserve-saas-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python app/initial_data.py
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Add **Environment Variables**:
   - `SECRET_KEY`: `<Generate a secure random string>`
   - `DATABASE_URL`: `sqlite:///./homeserve.db` (or your Cloud MySQL connection URL)
   - `RAZORPAY_KEY_ID`: `rzp_test_placeholder_key`
   - `RAZORPAY_KEY_SECRET`: `rzp_test_placeholder_secret`
6. Click **Create Web Service**.
7. Note down your Render backend URL (e.g. `https://homeserve-saas-backend.onrender.com`).

---

## 3. Deploying Frontend to Netlify

1. Log in to [Netlify](https://app.netlify.com).
2. Click **Add new site** -> **Import an existing project**.
3. Select **GitHub** and authorize your repository.
4. Configure Build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
5. Add **Environment Variables**:
   - `VITE_API_URL`: `https://homeserve-saas-backend.onrender.com/api/v1`
6. Click **Deploy Site**.
7. Your frontend will be live on a `*.netlify.app` domain!

---

## 4. (Optional) Connecting Cloud MySQL Database
To use production MySQL (e.g., Aiven, TiDB Serverless, Supabase, or Railway):
1. Create a MySQL database instance.
2. In your Render backend service, set:
   ```env
   DATABASE_URL="mysql+pymysql://<user>:<password>@<host>:3306/<database>?ssl_ca=/etc/ssl/cert.pem"
   ```
3. Restart the service. SQLAlchemy will automatically connect, generate all tables, and seed initial records.
