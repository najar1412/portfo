import os

from flask import render_template, redirect, request, session, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename

from module import model
from forms import LoginForm, RegistrationForm, UploadForm
from config import Config
import flaskapp
from module.utilities import ManageImage, ManageFolio


login_manager = LoginManager(flaskapp.app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return model.User.query.get(int(id))


def first_time_run():
    users = model.User.query.all()
    if len(users) == 0:
        return True

    else:
        return False


def portfo_cookie(session, portfo_title, portfo_caption, portfo_title_enable, portfo_caption_enable):
    session['portfo_title'] = portfo_title
    session['portfo_caption'] = portfo_caption
    session['portfo_title_enable'] = portfo_title_enable
    session['portfo_caption_enable'] = portfo_caption_enable

    return session


@flaskapp.app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = model.User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        folio = ManageFolio(flaskapp.db).new()
        flaskapp.db.session.add(user)
        flaskapp.db.session.commit()

        portfo_cookie(session, folio.title, folio.caption, folio.enable_title, folio.enable_caption)

        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))

    if first_time_run():
        return render_template('register.html', title='Register', form=form)

    return redirect(url_for('index'))


@flaskapp.app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = model.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')

            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('admin'))

    return render_template('login.html', title='Sign In', form=form)


@flaskapp.app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


@flaskapp.app.route('/')
def index():
    # TODO: refactor cookie session
    if first_time_run():
        return redirect('/register')

    else:
        # folio = model.Folio.query.filter_by(id=1).first()
        folio = ManageFolio().get_by_id(id=1)
        session['portfo_title'] = folio.title
        session['portfo_caption'] = folio.caption
        
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
    # TODO: refactor upload code to utilities
    form = UploadForm()
    if form.validate_on_submit() and 'photo' in request.files:
        for f in request.files.getlist('photo'):
            filename = secure_filename(f.filename)
            f.save(os.path.join(flaskapp.app.config['UPLOAD_PATH'], filename))
            ManageImage(flaskapp.db).new(filename=filename)

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