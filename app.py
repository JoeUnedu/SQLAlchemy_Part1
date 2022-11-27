"""Blogly application."""

from flask import Flask, request, redirect, render_template, redirect, flash, session
# from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, db_add_user, db_edit_user, db_add_post, db_edit_post
from datetime import datetime

app = Flask(__name__)

# Flask and SQL Alchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SECRET!"
# debug = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def blogly_home():
    """ Blogly Home Page """

    return redirect("/users")


@app.route("/users")
def list_users():
    """ Blogly Users w/ Add New User button """

    db_users = User.query.all()

    return render_template("list_users.html", headline="Blogly Users", users=db_users)


@app.route("/users/new")
def add_user_form():
    """ Blogly Add New User Form """

    return render_template("add_user.html", headline="Add New Blogly User")


@app.route("/users/new", methods=["POST"])
def add_user_process():
    """ Process Blogly Add New User Form """

    # extract form data, add, commit, then redirect to /users
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    msg = db_add_user(first_name, last_name, image_url)

    flash(msg["text"], msg["severity"])

    return redirect("/users")


@app.route("/users/<int:user_id>")
def view_user(user_id):
    """ Show the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)
    # ??? do null values cause issues on the server side?
    # I see a lot of instances in the log where an incorrect
    # parameter is used by SQL Alchemy and they typically happen
    # on records with nulls.

    allow_delete = True if len(db_user.posts) == 0 else False
    return render_template("view_user.html", headline="Blogly User",
                           user=db_user, allow_delete=allow_delete)


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """ Edit the details about a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    return render_template("edit_user.html",
                           headline=f"Edit Blogly {db_user.get_full_name()}",
                           user=db_user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user_process(user_id):
    """ Process the edit of a single Blogly user """

    # extract form data, edit, commit, then redirect to /users
    first_name = request.form["first-name"].strip()
    last_name = request.form["last-name"].strip()
    image_url = request.form["image-url"].strip()

    msg = db_edit_user(user_id, first_name, last_name, image_url)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{user_id}")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user_process(user_id):
    """ Process the delete of a single Blogly user """

    db_user = User.query.get_or_404(user_id)

    db.session.delete(db_user)
    db.session.commit()

    return redirect("/users")


@app.route("/posts/<int:post_id>")
def view_post(post_id):
    """ Show the information in a post """

    db_post = Post.query.get_or_404(post_id)
    full_name = db_post.user.get_full_name()
    created_date = datetime.strftime(
        db_post.created_at, "%a %b %d, %Y %I:%M %p").replace(" 0", " ")
    return render_template("view_post.html",
                           headline=db_post.title,
                           post=db_post, user_full_name=full_name, created=created_date)


@app.route("/users/<int:user_id>/posts/new")
def add_post_form(user_id):
    """ Show form to add a post for user user_id. """
    user_data = {}
    user_data["id"] = user_id
    user_data["name"] = User.query.get(user_id).get_full_name()

    return render_template("add_post.html", headline=f"Add Post for { user_data['name'] }",
                           user=user_data)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def add_post_process(user_id):
    """ Process the add post form. The post is added and the user is
       redirected to the user detail page, /users/<user_id> """

    # extract form data, add post, commit, then redirect to /users
    post_title = request.form["post-title"]
    post_content = request.form["post-content"]

    msg = db_add_post(post_title, post_content, user_id)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{ user_id }")


@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """ Edit the details in a single post """

    post_data = {"id": post_id}
    db_post = Post.query.get_or_404(post_id)
    post_data["title"] = db_post.title
    post_data["content"] = db_post.content
    post_data["user_id"] = db_post.user_id

    return render_template("edit_post.html", headline="Add New Blogly User", post=post_data)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_process(post_id):
    """ Process the edit of a post. Return to users/<user_id> """

    # extract form data, commit, then redirect to /users
    f_title = request.form["post-title"].strip()
    f_content = request.form["post-content"].strip()

    # msg will also include a field for the user_id for routing.
    msg = db_edit_post(post_id, f_title, f_content)

    flash(msg["text"], msg["severity"])

    return redirect(f"/users/{msg['user_id']}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post_process(post_id):
    """ Process the delete of a single post """

    db_post = Post.query.get_or_404(post_id)
    user_id = db_post.user_id

    db.session.delete(db_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")
