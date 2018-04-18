"""
Contains all os, and database interaction
"""
import os

from flask import session
from werkzeug.utils import secure_filename

from module import model
from config import Config


class ManageImage():
    def __init__(self, db_session=None):
        self.db_session = db_session


    def _delete_image_from_server(self, filename):
        """deletes a file based on filename from flask upload dir
        filename: str, filename of image to delete
        
        return: boolean"""
        try:
            os.remove(os.path.join(Config.UPLOAD_PATH, filename))
            return True

        except FileNotFoundError as e:
            print(e)
            return False


    def _image_to_dict(self, obj):
        """returns dict repr of database row
        obj: sqlalchemy Image object
        """
        return {
            'id': obj.id,
            'name': obj.name,
            'caption': obj.caption,
            'date': obj.date,
            'featured': obj.featured,
            'filename': obj.filename,
            'private': obj.private
        }


    def new(self, filename=None, name=None, caption=None, date=None, featured=False, private=True):
        """creates a new database entry for an image
        filename: str, name of file and extension
        name: str, name of image
        caption: str, description of image
        date: NOT IMP
        featured: boolean, featured image
        private: boolean, public or not"""
        image = model.Image(name=str(name), caption=str(caption), date=str(date), featured=featured, filename=str(filename), private=private)

        self.db_session.session.add(image)
        self.db_session.session.commit()

        return image


    def delete_image(self, obj):
        """deletes image information from app
        obj: sqlalchemy Image object
        
        return: boolean"""
        if self._delete_image_from_server(obj.filename):
            self.db_session.session.delete(obj)
            self.db_session.session.commit()

            return True

        else:
            print('deleting image failed')

            return False

    
    def image_by_id(self, id):
        """queries database for a single row object
        id: int, id of row
        
        return: sqlalchemy Image object"""
        return model.Image.query.filter_by(id=id).first()


    def edit(self, id, dto_image):
        """handles editing images
        id: int, id of image to edit
        dto_image: dict, data to update image with

        return: sqlalchemy Image object"""
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
            try:
                self.delete_image(image)
            except:
                print('Image information not deleted')
        
        self.db_session.session.commit()


        return image


    def get_all(self, private=None):
        """retrieves all image objs from database
        private: boolean, filters results
        
        return: dict, dict repr of objects"""
        images = {}
        for image in model.Image.query.all():
            if private:
                if image.private:
                    images[image.id] = self._image_to_dict(image)

            if private == False:
                if image.private == False:
                    images[image.id] = self._image_to_dict(image)

            if private == None:
                images[image.id] = self._image_to_dict(image)

        return images


    def upload_images(self, images):
        for x in images:
            filename = secure_filename(x.filename)
            x.save(os.path.join(Config.UPLOAD_PATH, filename))
            self.new(filename=filename)


class ManageFolio():
    def __init__(self, db_session=None):
        self.db_session = db_session


    def new(self):
        """creates a new folio object in the database
        
        return: sqlalchemy Folio object"""
        folio = model.Folio()
        self.db_session.session.add(folio)
        self.db_session.session.commit()

        return folio


    def get_by_id(self, id):
        """retrieves sqlalchemy Folio object
        id: int, id of object
        
        return: sqlalchemy Folio object"""
        return model.Folio.query.filter_by(id=id).first()


    def edit(self, session, id, dto_folio):
        """handles editing of sqlalchemy Folio object
        id: int, id of object to edit
        dto_folio: dict, edits to make
        
        return: sqlalchemy Folio object"""
        # TODO: Imp a class for handling flask session object
        folio = self.get_by_id(id)

        if 'folio_title' in dto_folio and dto_folio['folio_title'] and dto_folio['folio_title'] != '':
            folio.title = dto_folio['folio_title']

        if 'folio_caption' in dto_folio and dto_folio['folio_caption'] and dto_folio['folio_caption'] != '':
            folio.caption = dto_folio['folio_caption']

        if 'folio_title_enable' in dto_folio and dto_folio['folio_title_enable'] == 'True':
            if folio.enable_title == False:
                folio.enable_title = True
                session['portfo_title_enable'] = True
            else:
                folio.enable_title = False
                session['portfo_title_enable'] = False
            

        if 'folio_caption_enable' in dto_folio and dto_folio['folio_caption_enable'] == 'True':
            if folio.enable_caption == False:
                folio.enable_caption = True
                session['portfo_caption_enable'] = True
            else:
                folio.enable_caption = False
                session['portfo_caption_enable'] = False
        
        self.db_session.session.commit()

        return folio


class ManageUser():
    def __init__(self, db_session=None):
        self.db_session = db_session


    def get_by_id(self, id):
        return model.User.query.get(int(id))


    def get_by_username(self, username):
        return model.User.query.filter_by(username=username).first()


    def get_by_email(self, email):
        return model.User.query.filter_by(email=email).first()


    def get_all(self):
        return model.User.query.all()


    def new(self, username, email, password):
        user = model.User(username=username, email=email)
        user.set_password(password)
        
        self.db_session.session.add(user)
        self.db_session.session.commit()

        return user


    def validate(self, username, password):
        user = self.get_by_username(username)
        if user is None or not user.check_password(password):
            return False
        
        return user


class CookieMonster():
    def __init__(self, cookie):
        self.cookie = cookie


    def new(self):
        # TODO: build new portfo cookie
        self.destroy()
        self.update()

        return session


    def destroy(self):
        try:
            self.cookie.pop('portfo_title', None)
            self.cookie.pop('portfo_caption', None)
            self.cookie.pop('portfo_title_enable', None)
            self.cookie.pop('portfo_caption_enable', None)
        except:
            pass


    def update(self):
        folio = ManageFolio().get_by_id(id=1)

        session['portfo_title'] = folio.title
        session['portfo_caption'] = folio.caption
        session['portfo_title_enable'] = folio.enable_title
        session['portfo_caption_enable'] = folio.enable_caption

        return session

