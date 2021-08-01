from .base import *

ALLOWED_HOSTS = ["customfpl.pythonanywhere.com"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-bj+(xr*n5rk@(0))ntjfe*y63*rpacb7@rw2x6li9f@ryhlzk6"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
