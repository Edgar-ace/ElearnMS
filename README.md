# eStudy — E-Learning Management System

eStudy is a Django web application for managing online courses, enrollments, payments, lesson resources, and learning progress.

## Group members

Project group members:

| Full name | Student / registration number |
| --- | --- |
| Shema Edgar Israel | 224-063011-29766 |
| Sserunjogi Fahid | 224-063011-31849 |
| Famba Nasulu | 224-063011-29265 |

## Features

- Separate student, instructor, and administrator experiences.
- Course browsing and student enrollment.
- Payment submission and administrator payment verification.
- Lesson resources and lesson progress tracking.
- Role-based access to records and dashboards.

## Technology

- Python and Django
- SQLite for local development; PostgreSQL for the Render deployment
- Gunicorn for the production application server
- WhiteNoise for production static files

## Run locally

1. Create and activate a virtual environment.

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies and apply migrations.

   ```powershell
   py -m pip install -r requirements.txt
   py manage.py migrate
   ```

3. Start the development server.

   ```powershell
   py manage.py runserver
   ```

4. Open `http://127.0.0.1:8000/`.

Create a local Django administrator when needed:

```powershell
py manage.py createsuperuser
```

## Deploy to Render

The included `render.yaml` defines a Django web service and PostgreSQL database. The `build.sh` script installs dependencies, collects static files, and applies migrations during each build.

1. Push this project to a GitHub repository (see the Git instructions below).
2. In Render, choose **New → Blueprint** and connect the GitHub repository.
3. Review the services defined in `render.yaml` and apply the blueprint.
4. After the first deployment, open the web service's Shell and create the production administrator:

   ```bash
   python manage.py createsuperuser
   ```

5. Open the deployed `onrender.com` address and verify the site.

The production database is separate from the local SQLite database, so local records are not copied automatically. Add production records through the deployed admin or provide a reviewed data-import plan before deployment.

## Push to GitHub

If the local project has not been connected to the empty GitHub repository yet, run these commands from the project root. Replace the URL with the repository's HTTPS or SSH URL.

```powershell
git init -b main
git add .
git status
git commit -m "Prepare eStudy for deployment"
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Review `git status` before committing. The local virtual environment, SQLite database, imported SQL dump, and `.env` secrets are excluded by `.gitignore`.
