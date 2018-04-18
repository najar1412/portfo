"""
Contains all view function code
"""

import os

from flask import render_template, redirect, request, session, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from forms import LoginForm, RegistrationForm, UploadForm
import flaskapp
from module.utilities import ManageImage, ManageFolio, CookieMonster, ManageUser


login_manager = LoginManager(flaskapp.app)
login_manager.login_view = 'login'

# helpers
@login_manager.user_loader
def load_user(id):
    return ManageUser().get_by_id(id)


def first_time_run():
    users = ManageUser().get_all()
    if len(users) == 0:
        return True

    else:
        return False


@flaskapp.app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        ManageUser(flaskapp.db).new(username=form.username.data, email=form.email.data, password=form.password.data)
        ManageFolio(flaskapp.db).new()
        CookieMonster(session).new()

        return redirect(url_for('login'))

    if first_time_run():
        return render_template('register.html', form=form)

    return redirect(url_for('index'))


@flaskapp.app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = ManageUser().validate(form.username.data, form.password.data)
        if not user:
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('admin'))

    return render_template('login.html', form=form)


@flaskapp.app.route('/logout')
def logout():
    logout_user()
    CookieMonster(session).destroy()

    return redirect(url_for('index'))


@flaskapp.app.route('/')
def index():
    if first_time_run():
        return redirect('/register')

    else:
        if 'portfo_title' not in session:
            CookieMonster(session).new()
        
        images = ManageImage().get_all(private=False)

        return render_template('index.html', images=images)


@flaskapp.app.route('/admin')
@login_required
def admin():
    form = UploadForm()
    images = ManageImage().get_all()

    return render_template('admin.html', images=images, form=form)


@flaskapp.app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit() and 'photo' in request.files:
        ManageImage(flaskapp.db).upload_images(request.files.getlist('photo'))

        return redirect('/admin')

    return render_template('upload.html', form=form)


@flaskapp.app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_image(id):
    form = request.form
    ManageImage(flaskapp.db).edit(id, form)

    return redirect('/admin')


@flaskapp.app.route('/admin/edit/folio/<int:id>', methods=['GET', 'POST'])
def admin_edit_folio(id):
    form = request.form
    ManageFolio(flaskapp.db).edit(session, id, form)

    return redirect('/admin')


if __name__ == '__main__':
    flaskapp.app.run(debug=True)