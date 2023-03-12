from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)
from werkzeug.security import check_password_hash, generate_password_hash  # noqa

from app import create_app, db, logger, login_manager
from app.models import User
from app.auth import is_safe_url
from app.queries import get_user
from app.updates import db_update_user_password

app = create_app()


@app.route('/')
def index():
    """ Top level """
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = False
        if 'remember_me' in request.form.keys():
            remember_me = True
        error = None
        user = get_user(db, username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.to_dict()['password'], password):
            error = 'Incorrect password.'

        if error is None:
            login_user(user, remember=remember_me)
            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)

            return redirect(url_for('main'))

        flash(error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        error = None

        user = get_user(db, session.get('user_id'))
        if not check_password_hash(user.to_dict()['password'], old_password):
            error = 'Incorrect current password'
        elif new_password != confirm_password:
            error = 'New and confirming new passwords do not match'

        if error is None:
            db_update_user_password(db, user.username, new_password)
            flash('Password changed')
            return redirect(url_for('main'))

        flash(error)

    return render_template('change_password.html')


@app.route('/main')
@login_required
def main():
    """ Main landing page where the user gets a chance to choose the media library to examine """

    return render_template('media_selection.html')


if __name__ == '__main__':
    # TODO: Turn off debugging by default once production ready
    logger.info('Running from app.app main')
    app.run(debug=True)  # nosec
