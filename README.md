# 💧 Water Monitoring System

A Django-based web application for monitoring water quality data, featuring real-time status, data logging, API endpoints, and data export functionality.

- Secure login and session management  
- Live status of water quality metrics (pH, flow, etc.)  
- Automatic and manual data entry  
- Download data (PDF & Excel)  
- Admin panel with user management  
- REST API endpoints for external access  
- Session timeout and login protection middleware  

---

Project URLs:

/accounts/login/ → Login Page  
/ → Dashboard  
/data-entry/ → Automatic Data Generation  
/live-status/ → Live Status Monitoring  
/download/ → Download Data (PDF/Excel)  
/add-data/ → Manual Data Entry  
/admin/ → Django Admin Panel  
/admin/auth/user/ → Manage Users  
/admin/monitoring_app/waterqualitydata/ → View Last Added Data  
/api/water-quality/ → API: Last Updated Data  
/api/water-quality/?user_id=1 → API: Data for Specific User  

---

Installation & Setup:

```bash
git clone https://github.com/JayRajane/waterqualitymonitoring.git
cd water_monitoring_system

python -m venv env
env\Scripts\activate  # For Windows

pip install -r requirements.txt
# OR install manually
pip install django==5.1.7
pip install djangorestframework
pip install django-cors-headers
pip install pandas openpyxl xhtml2pdf

python manage.py makemigrations
python manage.py migrate
python manage.py runserver

python manage.py createsuperuser
```

---

Folder Structure:

```
water_monitoring_system/
├── monitoring_app/                # Your main Django app with models, views, etc.
├── staticfiles/                   # Static files (CSS, JS, images)
├── water_monitoring_system/       # Project-level settings (settings.py, urls.py, etc.)
├── db.sqlite3                     # Default SQLite database
├── manage.py                      # Django project manager script
├── requirements.txt               # Project dependencies

```

---

Notes:

- Timezone set to Asia/Kolkata  
- Session timeout set to 30 minutes  
- Login required for all views  
- Data export available in Excel and PDF formats  
