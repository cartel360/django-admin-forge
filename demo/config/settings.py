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
    "brand_name": "Django Admin Forge",
    "brand_logo_text": "DAF",
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
        "demo_app.subscription": "receipt",
        "demo_app.apikey": "key",
        "demo_app.invoice": "credit-card",
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
    "dashboard_quick_links": [
        {"label": "Applications", "url_name": "admin:forge-applications", "icon": "layers"},
        {"label": "Users", "url_name": "admin:auth_user_changelist", "icon": "user"},
        {"label": "Groups", "url_name": "admin:auth_group_changelist", "icon": "users"},
        {"label": "Customers", "url_name": "admin:demo_app_customer_changelist", "icon": "building"},
    ],
    "system_health_metrics": [
        {"metric": "uptime"},
        {"metric": "django_version"},
        {"metric": "database", "alias": "default"},
        {"metric": "cache", "alias": "default"},
        {"metric": "debug"},
    ],
    "dashboard_recent_records": {
        "title": "Recent customers",
        "model": "demo_app.Customer",
        "icon": "building",
        "limit": 5,
        "order_by": "-created_at",
        "primary_field": "company_name",
        "secondary_field": "contact_email",
        "meta_field": "plan",
    },
    "needs_attention": {
        "display": {"mode": "hybrid", "max_rows": 5},
        "rules": [
            {
                "id": "inactive-customers",
                "type": "bool_flag",
                "title": "Inactive customers",
                "model": "demo_app.Customer",
                "field": "is_active",
                "value": False,
                "level": "warning",
                "icon": "building",
                "cta": "Review",
            },
            {
                "id": "large-customers",
                "type": "numeric_threshold",
                "title": "Large customers",
                "model": "demo_app.Customer",
                "field": "seats",
                "op": ">=",
                "value": 25,
                "level": "info",
                "icon": "users",
                "cta": "View",
            },
            {
                "id": "subscriptions-expiring",
                "type": "date_due",
                "title": "Subscriptions expiring soon",
                "model": "demo_app.Subscription",
                "field": "expires_at",
                "window_days": 21,
                "direction": "within_or_past",
                "level": "danger",
                "icon": "clock",
                "cta": "Review",
            },
            {
                "id": "overdue-invoices",
                "type": "date_due",
                "title": "Overdue invoices",
                "model": "demo_app.Invoice",
                "field": "due_date",
                "direction": "past",
                "window_days": 0,
                "level": "warning",
                "icon": "receipt",
                "cta": "Open",
            },
            {
                "id": "inactive-api-keys",
                "type": "bool_flag",
                "title": "Inactive API keys",
                "model": "demo_app.ApiKey",
                "field": "is_active",
                "value": False,
                "level": "info",
                "icon": "key",
                "cta": "View",
            },
        ],
    },
}
