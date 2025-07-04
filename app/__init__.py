from dotenv import load_dotenv
import logging
import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf import CSRFProtect
from sqlalchemy import inspect

from app.musicmedia.musicmedia_objects import MEDIA

import config

DEFAULT_SECRET_KEY = 'you-will-never-guess'  # nosec
MAX_CSP_VIOLATIONS_REPORT_LENGTH = 1000
CSP_VIOLATIONS_REPORT_HEADER = 'CSP Violations Report'
VALID_SAFE_SITES = ['\'self\'',
                    'cdnjs.cloudflare.com',
                    'cdn.jsdelivr.net',
                    'cdn.datatables.net',
                    'code.jquery.com']

# Load local environment
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger()

# Initialize services
bootstrap = Bootstrap5()
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

    if app.env == 'Test' or app.config['SQLALCHEMY_DATABASE_URI'] == '':
        # Set up sqlite database acess
        logger.info('Using SQLite Database')
        db_file = app_name + '_test.db'

        try:
            os.unlink(app.root_path + os.sep + db_file)  # Forecefully remove any old debris
        except FileNotFoundError:
            pass
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file

    if 'SQLALCHEMY_DATABASE_URI' in list(app.config.keys()):
        logger.info('SQLALCHEMY_DATABASE_URI set')
    else:
        logger.info('SQLALCHEMY_DATABASE_URI not set!!!')

    if config.LOCAL_DEVELOPMENT:
        logger.info('Local development initiated. Trusted sites: {}'.format(app.config['CSRF_TRUSTED_ORIGINS']))

    # Turn off SQL modificationt tracking
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Load in the music media html file
    if app.config.get('MUSIC_MEDIA_HTML_FILE', None) is not None:
        MEDIA.from_html_file(app.config['MUSIC_MEDIA_HTML_FILE'])
    if app.config.get('MUSIC_MEDIA_HTML_FILE_RETENTION_COUNT') is not None:
        MEDIA.set_html_file_rentention_count(app.config['MUSIC_MEDIA_HTML_FILE_RETENTION_COUNT'])

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    # Set up the routes to the AJAX data api
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Set up the routes to the LPs library
    from app.lps import lps as lps_blueprint
    app.register_blueprint(lps_blueprint)

    # Set up the routes to the DVD library
    from app.dvds import dvds as dvds_blueprint
    app.register_blueprint(dvds_blueprint)

    # Set up the routes to the CDs library
    from app.cds import cds as cds_blueprint
    app.register_blueprint(cds_blueprint)

    # Set up the routes to the MINI CDs library
    from app.mini_cds import mini_cds as mini_cds_blueprint
    app.register_blueprint(mini_cds_blueprint)

    # Set up the routes to the ELPs library
    from app.elps import elps as elps_blueprint
    app.register_blueprint(elps_blueprint)

    # Set up the routes to the Cassettes library
    from app.cassettes import cassettes as cassettes_blueprint
    app.register_blueprint(cassettes_blueprint)

    # Setting up the security policay which, besides reasons of safety,
    # is used to force https.
    #   1. Note that need to add boostrap and other
    #      required external resources to the list of safe sites
    #   2. Inline scripts will require a "nonce" tag (see templates
    #      for examples)
    csp = {'default-src': VALID_SAFE_SITES,
           'script-src': VALID_SAFE_SITES,
           'script-src-elem': VALID_SAFE_SITES,
           'script-src-attr': VALID_SAFE_SITES,
           'style-src-attr': VALID_SAFE_SITES,
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
            logger.info('In DB change code chanegs')
            from app.demo_helpers import load_demo_data
            db.create_all()
            load_demo_data(db)
            from app.models import load_initial_users
            load_initial_users(db)

    logger.info('Flask application initialized: {0}'.format(app_name))
    app.logger = logger
    return app
