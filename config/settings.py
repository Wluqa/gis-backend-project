
from pathlib import Path
import os
import glob

# === ЖЁСТКАЯ НАСТРОЙКА ПУТЕЙ К GIS-БИБЛИОТЕКАМ ===
# Замени пути на те, что вывел PowerShell в Шаге 1!
GDAL_LIBRARY_PATH = r"C:\Users\Lenovo\miniconda3\envs\GIS\Library\bin\gdal.dll"  # ← ВСТАВЬ СВОЙ ПУТЬ
GEOS_LIBRARY_PATH = r"C:\Users\Lenovo\miniconda3\envs\GIS\Library\bin\geos_c.dll"   # ← ВСТАВЬ СВОЙ ПУТЬ (обычно рядом)
PROJ_LIB = os.path.join(os.environ.get("CONDA_PREFIX", r"C:\Users\Lenovo\miniconda3\envs\GIS"), "Library", "share", "proj")

# Добавляем папку с .dll в системный PATH, чтобы Windows их подхватила
lib_bin = os.path.dirname(GDAL_LIBRARY_PATH)
os.environ["PATH"] = lib_bin + os.pathsep + os.environ.get("PATH", "")
os.environ["GDAL_DATA"] = os.path.join(os.environ.get("CONDA_PREFIX", r"C:\Users\Lenovo\miniconda3\envs\GIS"), "Library", "share", "gdal")
# === КОНЕЦ НАСТРОЙКИ ===
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9op*lmgey8$gu$#dpn#7-dd)+_5(d3s=g#-b##$1+-d!8(%#e4'

DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # Поддержка гео-функций (PostGIS)
    'rest_framework',  # Django REST Framework для API
    'buildings',  # Наше приложение с моделями зданий
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gis_db',
        'USER': 'postgres',
        'PASSWORD': '12345678',  # ← ВПИШИ СВОЙ ПАРОЛЬ ОТ POSTGRES
        'HOST': 'localhost',  # Сервер БД (локально)
        'PORT': '5432',  # Стандартный порт PostgreSQL
    }
}

# === НАСТРОЙКИ DJANGO REST FRAMEWORK ===
REST_FRAMEWORK = {
    # Отключаем пагинацию (по заданию не требуется)
    'DEFAULT_PAGINATION_CLASS': None,
    # Разрешаем любые запросы (для тестового задания; в продакшене — токен/сессия)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # Если используешь drf-gis для фильтрации по расстоянию
    # 'DEFAULT_FILTER_BACKENDS': [
    #     'rest_framework_gis.filters.DistanceFilter',
    # ],
}

# === ПУТИ К GIS-БИБЛИОТЕКАМ (Windows + Conda) ===
# Django на Windows не всегда сам находит GDAL/GEOS/PROJ .dll файлы
# Этот код автоматически ищет их в активном conda-окружении

# Путь к conda-окружению (берём из переменной среды или задаём вручную)
conda_prefix = os.environ.get("CONDA_PREFIX")
if not conda_prefix:
    # ← Если CONDA_PREFIX не подхватился, впиши путь вручную:
    conda_prefix = r"C:\Users\Lenovo\miniconda3\envs\geo_env"

# Поиск GDAL (версия может быть gdal309.dll, gdal310.dll и т.д.)
gdal_pattern = os.path.join(conda_prefix, "Library", "bin", "gdal*.dll")
gdal_files = glob.glob(gdal_pattern)
if gdal_files:
    GDAL_LIBRARY_PATH = gdal_files[0]

# Поиск GEOS (geos_c.dll)
geos_pattern = os.path.join(conda_prefix, "Library", "bin", "geos_c*.dll")
geos_files = glob.glob(geos_pattern)
if geos_files:
    GEOS_LIBRARY_PATH = geos_files[0]

# Путь к PROJ (для систем координат)
PROJ_LIB = os.path.join(conda_prefix, "Library", "share", "proj")

# === ВАЛИДАЦИЯ ПАРОЛЕЙ (стандартные правила Django) ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === ИНТЕРНАЦИОНАЛИЗАЦИЯ ===
LANGUAGE_CODE = 'ru-ru'  # Русский язык интерфейса (опционально)
TIME_ZONE = 'Europe/Moscow'  # Часовой пояс Москва (или твой)
USE_I18N = True  # Включить интернационализацию
USE_TZ = True  # Использовать timezone-aware датирование

# === СТАТИЧЕСКИЕ ФАЙЛЫ ===
STATIC_URL = 'static/'

# === НАСТРОЙКИ ПО УМОЛЧАНИЮ ДЛЯ PRIMARY KEY (опционально, но удобно) ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'