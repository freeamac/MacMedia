import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
pagedown = PageDown()

app_name = 'MacMovies'

def create_app():
    app = Flask(app_name)

    # Set up sqlite database acess
    db_file = app_name + '_test.db'

    try:
        os.unlink(db_file) # Forecefully remove any old debris
    except FileNotFoundError:
        pass
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)

    # Set up the routes to the AJAX data api
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Set up the routes to the DVDs library
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

    with app.app_context():
        from app.demo_helpers import load_demo_data
        db.create_all()
        load_demo_data(db)

    return app

app = create_app()

@app.route('/')
def index():
    """ Main landing page where the user gets a chance to choose the media library to examine """
    print('Calling media_selection template')

    return render_template('media_selection.html')
 