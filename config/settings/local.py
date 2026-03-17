from config.settings.base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = str(BASE_DIR / "media")
MARTOR_UPLOAD_PATH = "martor"

INTERNAL_IPS = [
    "127.0.0.1",
]
