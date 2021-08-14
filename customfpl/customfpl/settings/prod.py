from .base import *

ALLOWED_HOSTS = ["antifpl.pythonanywhere.com"]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "kg6xcyia-i*e&+aeew5ca^ig&n9+#8sk8k+d*!j6)pfxz*tp30"

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
