"""
Contains all view function code
"""
import os

from flask import render_template, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user

import app
from forms import LoginForm, RegistrationForm, UploadForm
from module.utilities import ManageImage, ManageFolio, CookieMonster, ManageUser


# helpers
@app.login_manager.user_loader
def load_user(id):
    return ManageUser().get_by_id(id)


def first_time_run():
    users = ManageUser().get_all()
    if len(users) == 0:
        return True

    else:
        return False


@app.app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        ManageUser(app.db).new(username=form.username.data, email=form.email.data, password=form.password.data)
        ManageFolio(app.db).new()
        CookieMonster(session).new()

        return redirect(url_for('login'))

    if first_time_run():
        return render_template('register.html', form=form)

    return redirect(url_for('index'))


@app.app.route('/login', methods=['GET', 'POST'])
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


@app.app.route('/logout')
def logout():
    logout_user()
    CookieMonster(session).destroy()

    return redirect(url_for('index'))


@app.app.route('/')
def index():
    if first_time_run():
        return redirect('/register')

    else:
        if 'portfo_title' not in session:
            CookieMonster(session).new()
        
        images = ManageImage().get_all(private=False)

        return render_template('index.html', images=images)


@app.app.route('/admin')
@app.login_required
def admin():
    form = UploadForm()
    images = ManageImage().get_all()

    return render_template('admin.html', images=images, form=form)


@app.app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit() and 'photo' in request.files:
        ManageImage(app.db).upload_images(request.files.getlist('photo'))

        return redirect('/admin')

    return render_template('upload.html', form=form)


@app.app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_image(id):
    form = request.form
    ManageImage(app.db).edit(id, form)

    return redirect('/admin')


@app.app.route('/admin/edit/folio/<int:id>', methods=['GET', 'POST'])
def admin_edit_folio(id):
    form = request.form
    ManageFolio(app.db).edit(session, id, form)
    CookieMonster(session).update()

    return redirect('/admin')


if __name__ == '__main__':
    app.app.run(debug=True)