# Deploying the PDF Application (Alternatives)

If Render.com didn't work for you, here are two easier and very reliable alternatives.

## Option 1: PythonAnywhere (Best for Permanent Hosting)
PythonAnywhere is built specifically for Flask apps and is very beginner-friendly.

1.  **Sign Up**: Go to [www.pythonanywhere.com](https://www.pythonanywhere.com/) and create a free "Beginner" account.
2.  **Upload Code**:
    *   Go to the **Files** tab.
    *   Upload a ZIP of your `pdf_extractor` folder and unzip it, or use the **Bash Console** to clone your git repo.
3.  **Install Dependencies**:
    *   Open a **Bash Console**.
    *   Run: `pip3.10 install --user -r requirements.txt` (Make sure to use the python version matching your web app config).
4.  **Configure Web App**:
    *   Go to the **Web** tab.
    *   Click **Add a new web app**.
    *   Choose **Flask** -> **Python 3.10** (or latest).
    *   **Path**: Enter the path to your folder (e.g., `/home/yourusername/pdf_extractor/app.py`).
    *   **WSGI Configuration**: The auto-generated file usually works, but ensure it imports your app correctly (`from app import app as application`).
5.  **Reload**:
    *   Click the green **Reload** button at the top of the Web tab.
    *   Your site is live at `yourusername.pythonanywhere.com`.

## Option 2: ngrok (Best for Quick Sharing)
If you just want to show someone the app *right now* without setting up a server, use ngrok to share your local computer's connection.

1.  **Download**: Get ngrok from [ngrok.com](https://ngrok.com/download).
2.  **Run your App**: 
    *   Open your terminal/command prompt.
    *   Run `python app.py` (make sure it's running on localhost:5000).
3.  **Start Tunnel**:
    *   Open a *new* terminal window.
    *   Run: `ngrok http 5000`
4.  **Share**:
    *   Copy the `https://xxxx.ngrok-free.app` link it gives you.
    *   Anyone can open that link to use your app as long as your computer is on.

## Option 3: Run Locally (Production Mode)

If you have your own server:

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run with Waitress (Windows)**:
    *   Install: `pip install waitress`
    *   Run: `waitress-serve --listen=*:8000 app:app`

## Features Included
*   **PDF Extractor**: `/`
*   **PDF Generator**: `/generate-page`
*   **Direct Fill**: `/direct-fill-page`
*   **Patient Matcher**: `/patient-matcher`
