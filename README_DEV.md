Developer quick start

This project is configured to run locally without Cloudinary by providing a local media fallback.

Steps to run locally (Windows PowerShell):

1. Copy example env and edit values if needed

   cp .env.example .env

2. Create and activate a venv (use `venv` or `.venv` consistently)

   python -m venv .venv

   # PowerShell (dot-source the PowerShell activation script)
   . .\.venv\Scripts\Activate.ps1

   # If you prefer the old cmd.exe activation (or run from Command Prompt):
   # .\.venv\Scripts\activate.bat

   # Troubleshooting: PowerShell may block script execution. To allow the
   # virtualenv activation script for the current session, run:
   # Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

3. Upgrade pip and install requirements

   python -m pip install --upgrade pip
   pip install -r requirements.txt

4. Apply database migrations

   cd si2_2doParcial_Backend
   python manage.py migrate

5. (Optional) Create a superuser

   python manage.py createsuperuser

6. Run the development server

   python manage.py runserver

Notes:
- If you want to use Cloudinary for media, set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in your `.env`. When present the project will use Cloudinary automatically.
- For CORS, edit `CORS_ALLOWED_ORIGINS` in `.env` (comma-separated). When set, the server will disable wildcard origin and use the provided list; this is required if you send credentials from the browser.
- Media files will be stored in `./media/` when Cloudinary is not configured.

Troubleshooting:
- If you get CORS errors in the browser, open DevTools -> Network and inspect the OPTIONS preflight response headers.
- Make sure `django-cors-headers` is installed (it's in requirements.txt). If missing: `pip install django-cors-headers`.
