# Deploying the PDF Application (with Patient Matcher)

Your application is now a unified web app that includes the Extractor, Generator, Direct Fill, and Patient Matcher. It is configured to run on cloud platforms like **Render** or **Heroku**.

## Option 1: Render.com (Recommended & Free)

1.  **Push to GitHub**:
    *   Ensure your `pdf_extractor` folder is in a GitHub repository.

2.  **Create Service**:
    *   Go to [dashboard.render.com](https://dashboard.render.com/).
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub repository.

3.  **Configure**:
    *   **Root Directory**: `rramessur/pdf_extractor` (or wherever your `app.py` is).
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn app:app`
    *   **Instance Type**: Free

4.  **Deploy**:
    *   Click **Create Web Service**.
    *   Your app will be live at a URL like `https://my-pdf-app.onrender.com`.

## Option 2: Run Locally (Production Mode)

If you want to run it on your own server:

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run with Gunicorn (Linux/Mac)**:
    ```bash
    gunicorn app:app
    ```

3.  **Run with Waitress (Windows)**:
    *   Install: `pip install waitress`
    *   Run: `waitress-serve --listen=*:8000 app:app`

## Features Included
*   **PDF Extractor**: `/`
*   **PDF Generator**: `/generate-page`
*   **Direct Fill**: `/direct-fill-page`
*   **Patient Matcher**: `/patient-matcher`
