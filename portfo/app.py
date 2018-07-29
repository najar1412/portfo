"""
Contains all view function code
"""
import os

from flask import render_template, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user

import config
from forms import LoginForm, RegistrationForm, UploadForm
from module.utilities import ManageImage, ManageFolio, CookieMonster, ManageUser


# helpers
@config.login_manager.user_loader
def load_user(id):
    return ManageUser().get_by_id(id)


def first_time_run():
    users = ManageUser().get_all()
    if len(users) == 0:
        return True

    else:
        return False


@config.app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        ManageUser(config.db).new(username=form.username.data, email=form.email.data, password=form.password.data)
        ManageFolio(config.db).new()
        CookieMonster(session).new()

        return redirect(url_for('login'))

    if first_time_run():
        return render_template('register.html', form=form)

    return redirect(url_for('index'))


@config.app.route('/login', methods=['GET', 'POST'])
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


@config.app.route('/logout')
def logout():
    logout_user()
    CookieMonster(session).destroy()

    return redirect(url_for('index'))


@config.app.route('/')
def index():
    if first_time_run():
        return redirect('/register')

    else:
        if 'portfo_title' not in session:
            CookieMonster(session).new()
        
        images = ManageImage().get_all(private=False)

        return render_template('index.html', images=images)


@config.app.route('/admin')
@config.login_required
def admin():
    form = UploadForm()
    images = ManageImage().get_all()

    return render_template('admin.html', images=images, form=form)


@config.app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit() and 'photo' in request.files:
        ManageImage(config.db).upload_images(request.files.getlist('photo'))

        return redirect('/admin')

    return render_template('upload.html', form=form)


@config.app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_image(id):
    form = request.form
    ManageImage(config.db).edit(id, form)

    return redirect('/admin')


@config.app.route('/admin/public_all', methods=['GET', 'POST'])
def admin_public_all():
    ManageImage(config.db).public_all()

    return redirect('/admin')


@config.app.route('/admin/private_all', methods=['GET', 'POST'])
def admin_private_all():
    ManageImage(config.db).private_all()

    return redirect('/admin')


@config.app.route('/admin/edit/folio/<int:id>', methods=['GET', 'POST'])
def admin_edit_folio(id):
    form = request.form
    ManageFolio(config.db).edit(session, id, form)
    CookieMonster(session).update()

    return redirect('/admin')


if __name__ == '__main__':
    config.app.run(debug=True)