from flask import render_template

from app import create_app

app = create_app()

@app.route('/')
def index():
    """ Main landing page where the user gets a chance to choose the media library to examine """
    print('Calling media_selection template')

    return render_template('media_selection.html')