from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "demo-secret-key-only"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django_admin_forge",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "demo_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DJANGO_ADMIN_FORGE = {
    "brand_name": "django-admin-forge",
    "brand_logo_text": "FORGE",
    "brand_tagline": "Premium Django control plane",
    "accent_color": "green",
    "default_theme": "system",
    "show_sidebar_search": True,
    "enable_command_bar": True,
    "menu_icons": {
        "auth": "shield",
        "auth.user": "user",
        "auth.group": "users",
        "demo_app.customer": "building",
    },
    "menu_tabs": [
        {"label": "Dashboard", "url_name": "admin:index", "icon": "layout-grid"},
        {"label": "Applications", "url_name": "admin:forge-applications", "icon": "layers"},
    ],
    "dashboard_analytics_cards": [
        {
            "label": "Customers",
            "app_label": "demo_app",
            "model": "Customer",
            "metric": "count",
            "icon": "users",
            "hint": "Total customer records",
        },
        {
            "label": "Active customers",
            "app_label": "demo_app",
            "model": "Customer",
            "metric": "count",
            "queryset_filter": {"is_active": True},
            "icon": "activity",
            "hint": "is_active = true",
        },
        {
            "label": "Staff users",
            "app_label": "auth",
            "model": "User",
            "metric": "count",
            "queryset_filter": {"is_staff": True},
            "icon": "shield",
            "hint": "System operators",
        },
    ],
}
