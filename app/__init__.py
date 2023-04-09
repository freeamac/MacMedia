import logging
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from sqlalchemy import inspect

import config

DEFAULT_SECRET_KEY = 'you-will-never-guess'
MAX_CSP_VIOLATIONS_REPORT_LENGTH = 1000
CSP_VIOLATIONS_REPORT_HEADER = 'CSP Violations Report'

# Set up logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger()

bootstrap = Bootstrap()
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
moment = Moment()
pagedown = PageDown()

app_name = __name__


def create_app(name=None):
    logger.info(f'Starting app in {config.APP_ENV} environment')
    if name is None:
        app = Flask(app_name)
    else:
        app = Flask(name)
    app.env = config.APP_ENV

    # Import default settings
    logger.info('Loading config object config.{0}Config'.format(app.env))
    app.config.from_object('config.{0}Config'.format(app.env))

    if app.env in ['Test', 'Dev']:
        # Set up sqlite database acess
        db_file = app_name + '_test.db'

        try:
            os.unlink(app.root_path + os.sep + db_file)  # Forecefully remove any old debris
        except FileNotFoundError:
            pass
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file

    if 'SQLALCHEMY_DATABASE_URI' in list(app.config.keys()):
        logger.info('SQLALCHEMY_DATABASE_URI set to {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))
    else:
        logger.info('SQLALCHEMY_DATABASE_URI not set!!!')

    # Turn off SQL modificationt tracking
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    # Set up the routes to the AJAX data api
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Set up the routes to the DVD library
    from app.dvds import dvds as dvds_blueprint
    app.register_blueprint(dvds_blueprint)

    # Set up the routes to the CDs library
    from app.cds import cds as cds_blueprint
    app.register_blueprint(cds_blueprint)

    # Set up the routes to the Cassettes library
    from app.cassettes import cassettes as cassettes_blueprint
    app.register_blueprint(cassettes_blueprint)

    # Set up the routes to the LPs library
    from app.lps import lps as lps_blueprint
    app.register_blueprint(lps_blueprint)

    # Setting up the security policay which, besides reasons of safety,
    # is used to force https.
    #   1. Note that need to add boostrap and other
    #      required external resources to the list of safe sites
    #   2. Inline scripts will require a "nonce" tag (see templates
    #      for examples)
    csp = {'default-src': ['\'self\'',
                           'cdnjs.cloudflare.com',
                           'cdn.jsdelivr.net',
                           'cdn.datatables.net',
                           'code.jquery.com'],
           'script-src': ['\'self\'',
                          'cdnjs.cloudflare.com',
                          'cdn.jsdelivr.net',
                          'cdn.datatables.net',
                          'code.jquery.com'],
           'script-src-elem': ['\'self\'',
                               'cdnjs.cloudflare.com',
                               'cdn.jsdelivr.net',
                               'cdn.datatables.net',
                               'code.jquery.com'],
           'script-src-attr': ['\'self\'',
                               'cdnjs.cloudflare.com',
                               'cdn.jsdelivr.net',
                               'cdn.datatables.net',
                               'code.jquery.com'],
           'style-src-attr': ['\'self\'',
                              'cdnjs.cloudflare.com',
                              'cdn.jsdelivr.net',
                              'cdn.datatables.net',
                              'code.jquery.com'],
           }
    logger.info(f'Setting security content policy to {csp}')
    Talisman(app,
             content_security_policy=csp,
             content_security_policy_nonce_in=['script-src'],
             content_security_policy_report_only=True,
             content_security_policy_report_uri='/csp-report'
             )
    app.csp_violations = [CSP_VIOLATIONS_REPORT_HEADER]

    # TODO - Securely inject into environment for production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    if app.config['SECRET_KEY'] == DEFAULT_SECRET_KEY:
        logger.info('Secret key set to default value!')
    csrf.init_app(app)

    # Load in test/demo data if we do not have tables set up.
    # This is required in all in memory db environments and
    # first time instantiation of other persistent db engines
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('USERS'):
            from app.demo_helpers import load_demo_data
            db.create_all()
            load_demo_data(db)
            from app.models import load_initial_users
            load_initial_users(db)

    logger.info('Flask application initialized: {0}'.format(app_name))
    app.logger = logger
    return app
