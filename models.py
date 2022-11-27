"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy, time
# import flask_sqlalchemy

# # flask_sqlalchemy.time.gmtime()
# # time.struct_time(tm_year=2021, tm_mon=3, tm_mday=18, tm_hour=23, tm_min=32, tm_sec=20, tm_wday=3, tm_yday=77, tm_isdst=0)
# # datetime.strptime(
# #                 cookie_data_out["date_last_activity"], "%Y-%m-%d %H:%M:%S.%f")

db = SQLAlchemy()


def connect_db(app):
    """ Associate the flask application app with SQL Alchemy and 
        initialize SQL Alchemy
    """
    db.app = app
    db.init_app(app)


# MODELS
class User(db.Model):
    """ User model for blobly users table  """

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    first_name = db.Column(db.String(25),
                           nullable=False)

    # last_name is nullable -- Cher, Prince, Beyoncé
    last_name = db.Column(db.String(25),
                          nullable=True)

    image_url = db.Column(db.Text,
                          nullable=True)

    def __repr__(self):
        """Show info about user."""

        return f"<Blogly #{self.id} {self.first_name} {self.last_name} image url: {self.image_url} >"

    def get_full_name(self):
        """Get the full name """
        full_name = f"{self.first_name} {self.last_name}"

        return full_name.strip()


class Post(db.Model):
    """ User model for blobly users table  """

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.String(128),
                      nullable=False)

    content = db.Column(db.Text,
                        nullable=False)

    created_at = db.Column(db.DateTime(timezone=True),
                           default=time.strftime("%Y-%m-%d %H:%M:%S %z"),
                           nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'))

    user = db.relationship('User', backref='posts')

    def __repr__(self):
        """Show post information """

        return f"<Blogly #{self.id} title: '{self.title}' content: '{self.content}' created_at: {self.created_at} >"


def change_occurred(from_vals, to_vals):
    """ compares lists of from and to values to ensure a change occurred """

    if (len(from_vals) == len(to_vals)):
        for fr, to in zip(from_vals, to_vals):
            if (fr != to):
                return True
        # all from and to values matched. NO change occurred
        return False
    else:
        # The lengths of the lists should match.
        # For now, return True
        return True


def db_add_user(first_name, last_name, image_url):
    """ adds a user to the users table """

    msg = {}

    new_user = User(first_name=first_name.strip(),
                    last_name=last_name.strip(), image_url=image_url.strip())

    db.session.add(new_user)
    db.session.commit()

    msg["text"] = f"{new_user.get_full_name()} created."
    msg["severity"] = "okay"

    return msg


def db_add_post(title, content, user_id):
    """ adds a post to the posts table """

    msg = {}

    new_post = Post(title=title.strip(),
                    content=content.strip(),
                    user_id=user_id)

    db.session.add(new_post)
    db.session.commit()

    msg["text"] = f"{new_post.title} created."
    msg["severity"] = "okay"

    return msg


def db_edit_user(id, first_name, last_name, image_url):
    """ Updates the user when changes have occurred """

    db_user = User.query.get_or_404(id)

    msg = {}

    if (change_occurred([db_user.first_name, db_user.last_name, db_user.image_url],
                        [first_name, last_name, image_url])):

        db_user.first_name = first_name
        db_user.last_name = last_name
        db_user.image_url = image_url

        db.session.commit()

        msg["text"] = f"{db_user.get_full_name()} successfully updated."
        msg["severity"] = "okay"

    else:
        msg["text"] = f"There were no changes!"
        msg["severity"] = "warning"

    return msg


def db_edit_post(post_id, title, content):
    """ Updates the post when changes have occurred """

    db_post = Post.query.get_or_404(post_id)
    user_id = db_post.user.id

    msg = {"user_id": user_id}

    if (change_occurred([db_post.title, db_post.content], [title, content])):

        db_post.title = title
        db_post.content = content

        db.session.commit()

        msg["text"] = f"{db_post.title} successfully updated."
        msg["severity"] = "okay"

    else:
        msg["text"] = f"There were no changes!"
        msg["severity"] = "warning"

    return msg
