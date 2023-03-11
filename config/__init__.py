import os
from pathlib import Path
#import sys
#import config.settings

# Build paths inside the project like this: BASE_DIR / <subdir>
#BASE_DIR = Path(__file__).resolve().parent.parent
#STATICFILES_DIR = (str(BASE_DIR.joinpath('static')),)

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


class DevConfig(BaseConfig):
   FLASK_ENV = 'development'


class AzureConfig(BaseConfig):
   # Deployments to Azure should have the WEBSIT_HOSTNAME set in the environment
   ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []
   CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['WEBSITE_HOSTNAME']] if 'WEBSITE_HOSTNAME' in os.environ else []

   # Configure Postgres database based on connection string of the libpq keyword/value form:
   # https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
   if 'AZURE_POSGRESQL_CONNECTIONSTRING' in os.environ:  # Needed since this is evaluated in all environments
      conn_str = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
      conn_str_params = {pair.split('=')[0]: pair.split('=')[1] for pair in conn_str.split(' ')}

      SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
         dbuser=conn_str_params['user'],
         dbpass=conn_str_params['password'],
         dbhost=conn_str_params['host'],
         dbname=conn_str_params['dbname']
      )

   else:
      DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
         dbuser=os.getenv('DBUSER'),
         dbpass=os.getenv('DBPASS'),
         dbhost=os.getenv('DBHOST'),
         dbname=os.getenv('DBNAME')
      )

   

class StagingConfig(AzureConfig):
   FLASK_ENV = 'staging'
   DEBUG = False


class ProductionConfig(AzureConfig):
   FLASK_ENV = 'staging'
   DEBUG = False

class TestConfig(BaseConfig):
   FLASK_ENV = 'testing'
   TESTING = True
#SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/flask-deploy'
