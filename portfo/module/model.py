from werkzeug.security import generate_password_hash, check_password_hash

from flaskapp import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # flask-Login required methods
    @property
    def is_active(self):
        return True


    @property
    def is_authenticated(self):
        return True


    @property
    def is_anonymous(self):
        return False


    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')


    def __repr__(self):
        return '<User %r>' % self.username


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    caption = db.Column(db.String())
    date = db.Column(db.String())
    featured = db.Column(db.Boolean(), default=False)
    filename = db.Column(db.String())
    private = db.Column(db.Boolean(), default=True)


class Folio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), default="portfo v0.1.0")
    caption = db.Column(db.String(), default="Add a new caption!")
    enable_title = db.Column(db.Boolean(), default=True)
    enable_caption = db.Column(db.Boolean(), default=True)


db.create_all()
