import logging
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

import config


# Set up logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger()

bootstrap = Bootstrap()
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
    if 'SQLALCHEMY_DATABASE_URI' in list(app.config.keys()):
        logger.info('SQLALCHEMY_DATABASE_URI set to {}'.format(app.config['SQLALCHEMY_DATABASE_URI']))
    else:
        logger.info('SQLALCHEMY_DATABASE_URI not set!!!')

    if app.env in ['Test', 'Dev']:
        # Set up sqlite database acess
        db_file = app_name + '_test.db'

        try:
            os.unlink(app.root_path + os.sep + db_file)  # Forecefully remove any old debris
        except FileNotFoundError:
            pass
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file

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

    # TODO - Securely inject into environment for production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'you-will-never-guess')

    # Load in test/demo data in development environments
    if app.env not in ['staging', 'production']:
        with app.app_context():
            from app.demo_helpers import load_demo_data

            # Start with a clean slate ignore pass issues
            try:
                db.drop_all()
            except:
                pass

            db.create_all()
            load_demo_data(db)
            from app.models import load_initial_users
            load_initial_users(db)

    logger.info('Flask application initialized: {0}'.format(app_name))
    return app
