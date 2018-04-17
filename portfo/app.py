import os

from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from module import model
from forms import LoginForm, RegistrationForm
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return model.User.query.get(int(id))


def tmp_images():
    return os.listdir('static/img')


def new_image(Image, filename=None, name=None, caption=None, date=None, featured=False, private=True):
    image = Image(name=str(name), caption=str(caption), date=str(date), featured=featured, filename=str(filename), private=private)
    db.session.add(image)
    db.session.commit()


    return image


def build_tmp_images(db):
    images = tmp_images()
    for image in images:
        tmp_image = new_image(model.Image, filename=image, name=image, caption=f'{image}, {image}, {image}, {image}.', date='')
        db.session.add(tmp_image)
        db.session.commit()

    return images


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


def image_by_id(Image, id):
    return Image.query.filter_by(id=id).first()


def folio_by_id(id):
    return model.Folio.query.filter_by(id=id).first()


def db_edit_image(db, id, dto_image):
    image = image_by_id(model.Image, id)

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
    
    db.session.commit()


    return image


def db_edit_folio(db, id, dto_folio):
    folio = folio_by_id(id)

    if 'folio_title' in dto_folio and dto_folio['folio_title'] and dto_folio['folio_title'] != '':
        folio.title = dto_folio['folio_title']
    if 'folio_caption' in dto_folio and dto_folio['folio_caption'] and dto_folio['folio_caption'] != '':
        folio.caption = dto_folio['folio_caption']
    
    db.session.commit()

    return folio


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = model.User(username=form.username.data, email=form.email.data)
        folio = model.Folio(title='Portfo', caption='contact\ncontact\ncontact')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.add(folio)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route('/')
def index():
    # build_tmp_images(db)
    folio = model.Folio.query.filter_by(id=1).first()
    session['portfo_title'] = folio.title
    session['portfo_caption'] = folio.caption
    
    images = get_images(private=False)
    # images = {}

    return render_template('index.html', images=images)


@app.route('/admin')
@login_required
def admin():
    images = get_images()

    return render_template('admin.html', images=images)


@app.route('/test', methods=['GET', 'POST'])
def test():
    print('testing test')
    return redirect('/')


@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_image(id):
    form = request.form
    db_edit_image(db, id, form)

    return redirect('/admin')


@app.route('/admin/edit/folio/<int:id>', methods=['GET', 'POST'])
def admin_edit_folio(id):
    form = request.form
    print(form)
    # db_edit_image(db, id, form)
    db_edit_folio(db, id, form)

    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)