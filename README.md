# SuggestCVShapes

This repository contains a small Flask app that detects basic shapes in uploaded images using OpenCV.

Files added:
- app.py
- templates/index.html
- requirements.txt
- Procfile
- Dockerfile
- render.yaml (optional Render infra-as-code)
- .gitignore

Quick start (local):
1. python -m venv venv
2. source venv/bin/activate  # or venv\\Scripts\\activate on Windows
3. pip install -r requirements.txt
4. python app.py
5. Open http://localhost:5000

Deploy on Render (recommended using Docker):
1. Push this repo to GitHub (already done).
2. Create a new Web Service on Render and connect your GitHub repo.
   - Environment: Docker
   - Render will build using the provided Dockerfile.
3. Set environment variable SECRET_KEY in Render (service → Environment)

If you prefer Render's Python environment (no Docker), set in the Render UI:
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app --bind 0.0.0.0:$PORT

Notes:
- The app reads SECRET_KEY from the SECRET_KEY environment variable; please set it in Render for production.
- Dockerfile installs system libraries required by OpenCV to avoid runtime import errors.
