from typing_extensions import Required
from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app, db
from app.auth import load_logged_in_user, login_required
from app.queries import get_user
from app.updates import db_update_user_password

app = create_app()


@app.before_request
def load_user():
    load_logged_in_user()


@app.route('/')
def index():
    """ Top level """
    if g.user is None:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('main'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = get_user(db, username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.to_dict()['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.to_dict()['username']
            return redirect(url_for('main'))

        flash(error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


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
    app.run(debug=True)