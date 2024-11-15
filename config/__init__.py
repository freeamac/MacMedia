import os
from pathlib import Path
# import sys

# Build paths inside the project like this: BASE_DIR / <subdir>
# BASE_DIR = Path(__file__).resolve().parent.parent
# STATICFILES_DIR = (str(BASE_DIR.joinpath('static')),)

POSTGRES_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'

# Set the application environment based on the specified env
APP_ENV = os.environ.get('APP_ENV', 'Dev')


class BaseConfig():
    # Build paths inside the project like this: BASE_DIR / <subdir>
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATICFILES_DIR = (str(BASE_DIR.joinpath('static')),)
    API_PREFIX = '/api'
    STATIC_URL = 'static/'
    DEBUG = True
    TESTING = False
    MUSIC_MEDIA_DATA_DIR = None
    MUSIC_MEDIA_HTML_FILE = None
    MUSIC_MEDIA_HTML_FILE_RETENTION_COUNT = 20


LOCAL_DEVELOPMENT = 'DB_USER' in os.environ and 'DB_PASSWORD' in os.environ and 'DATABASE' in os.environ and os.environ['APP_ENV'] != 'Test'


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    ALLOWED_HOSTS = ['127.0.0.1'] if LOCAL_DEVELOPMENT else []
    CSRF_TRUSTED_ORIGINS = ['https://127.0.0.1', 'http://127.0.0.1'] if LOCAL_DEVELOPMENT else []
    if LOCAL_DEVELOPMENT:
        # Set up to connection to local postgreSQL database
        DATABASE_URI = POSTGRES_URI.format(dbuser=os.environ['DB_USER'],
                                           dbpass=os.environ['DB_PASSWORD'],
                                           dbhost="{}:{}".format(os.environ.get('DB_HOST', '127.0.0.1'), os.environ.get('DB_PORT', '5432')),
                                           dbname=os.environ['DATABASE'])
    else:
        DATABASE_URI = ''
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    MUSIC_MEDIA_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data')
    MUSIC_MEDIA_HTML_FILE = os.path.join(MUSIC_MEDIA_DATA_DIR, 'dev_music.html')


class AzureConfig(BaseConfig):
    # Deployments to Azure should have the WEBSIT_HOSTNAME set in the environment
    ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
    CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

    # Configure Postgres database based on connection string of the libpq keyword/value form:
    # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
    if 'AZURE_POSTGRESQL_CONNECTIONSTRING' in os.environ:  # Needed since this is evaluated in all environments
        conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
        conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

        DATABASE_URI = POSTGRES_URI.format(dbuser=conn_str_params['user'],
                                           dbpass=conn_str_params['password'],
                                           dbhost=conn_str_params['host'],
                                           dbname=conn_str_params['dbname'])

    else:
        DATABASE_URI = POSTGRES_URI.format(dbuser=os.getenv('DBUSER'),
                                           dbpass=os.getenv('DBPASS'),
                                           dbhost=os.getenv('DBHOST'),
                                           dbname=os.getenv('DBNAME'))
    SQLALCHEMY_DATABASE_URI = DATABASE_URI


class StagingConfig(AzureConfig):
   FLASK_ENV = 'staging'
   DEBUG = False


class ProductionConfig(AzureConfig):
   FLASK_ENV = 'production'
   DEBUG = False


class TestConfig(BaseConfig):
   FLASK_ENV = 'testing'
   TESTING = True
   WTF_CSRF_ENABLED = False