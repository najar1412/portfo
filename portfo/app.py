import os

from flask import render_template, redirect, request, session, url_for, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from module import model
from forms import LoginForm, RegistrationForm, UploadForm
from config import Config
import flaskapp


login_manager = LoginManager(flaskapp.app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return model.User.query.get(int(id))


def new_image(session, filename=None, name=None, caption=None, date=None, featured=False, private=True):
    image = model.Image(name=str(name), caption=str(caption), date=str(date), featured=featured, filename=str(filename), private=private)
    session.add(image)
    session.commit()

    return image


def delete_image_from_server(filename):
    # os.remove(os.path.join(Config.UPLOAD_PATH, filename))
    pass


def delete_image(row):
    delete_image_from_server(row.filename)

    return row


def _image_to_dict(Image):
    image = {
        'id': Image.id,
        'name': Image.name,
        'caption': Image.caption,
        'date': Image.date,
        'featured': Image.featured,
        'filename': Image.filename,
        'private': Image.private
    }

    return image


def get_images(private=None):
    images = {}
    for image in model.Image.query.all():
        if private:
            if image.private:
                images[image.id] = _image_to_dict(image)

        if private == False:
            if image.private == False:
                images[image.id] = _image_to_dict(image)

        if private == None:
            images[image.id] = _image_to_dict(image)

    return images


def image_by_id(id):
    return model.Image.query.filter_by(id=id).first()


def folio_by_id(id):
    return model.Folio.query.filter_by(id=id).first()


def db_edit_image(session, id, dto_image):
    image = model.Image.query.filter_by(id=id).first()

    if 'image_name' in dto_image and dto_image['image_name']:
        image.name = dto_image['image_name']

    if 'image_caption' in dto_image and dto_image['image_caption']:
        image.caption = dto_image['image_caption']

    if 'image_date' in dto_image and dto_image['image_date']:
        image.date = dto_image['image_date']

    if 'image_featured' in dto_image and dto_image['image_featured']:
        if dto_image['image_featured'] == 'True':
            image.featured = True

        elif dto_image['image_featured'] == 'False':
            image.featured = False

    if 'image_private' in dto_image and dto_image['image_private']:
        if dto_image['image_private'] == 'True':
            image.private = True

        elif dto_image['image_private'] == 'False':
            image.private = False

    if 'delete_image' in dto_image and dto_image['delete_image'] == 'True':
        session.session.delete(delete_image(image))
        session.session.commit()

        return True
    
    session.session.commit()


    return image


def db_edit_folio(session, id, dto_folio):
    folio = folio_by_id(id)

    if 'folio_title' in dto_folio and dto_folio['folio_title'] and dto_folio['folio_title'] != '':
        folio.title = dto_folio['folio_title']
    if 'folio_caption' in dto_folio and dto_folio['folio_caption'] and dto_folio['folio_caption'] != '':
        folio.caption = dto_folio['folio_caption']
    
    session.commit()

    return folio


@flaskapp.app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = model.User(username=form.username.data, email=form.email.data)
        folio = model.Folio(title='Portfo', caption='contact\ncontact\ncontact')
        user.set_password(form.password.data)
        flaskapp.db.add(user)
        flaskapp.db.add(folio)
        flaskapp.db.commit()

        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


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
    folio = model.Folio.query.filter_by(id=1).first()
    session['portfo_title'] = folio.title
    session['portfo_caption'] = folio.caption
    
    images = get_images(private=False)

    return render_template('index.html', images=images)


@flaskapp.app.route('/admin')
@login_required
def admin():
    form = UploadForm()
    images = get_images()

    return render_template('admin.html', images=images, form=form)


@flaskapp.app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit() and 'photo' in request.files:
        for f in request.files.getlist('photo'):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            new_image(flaskapp.db, filename=filename)
        return 'Upload completed.'

    return render_template('upload.html', form=form)


@flaskapp.app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_image(id):
    form = request.form
    db_edit_image(flaskapp.db, id, form)

    return redirect('/admin')


@flaskapp.app.route('/admin/edit/folio/<int:id>', methods=['GET', 'POST'])
def admin_edit_folio(id):
    form = request.form
    db_edit_folio(flaskapp.db, id, form)

    return redirect('/admin')


if __name__ == '__main__':
    flaskapp.app.run(debug=True)