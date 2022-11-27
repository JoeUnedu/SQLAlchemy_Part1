from unittest import TestCase

from app import app
from models import db, User, Post

# Use a test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class BloglyUserTests(TestCase):
    """Tests for Blogly User view, add, edit, and delete. """

    def setUp(self):
        """Add blogly user."""

        User.query.delete()

        new_user = User(first_name="Blogly Q.",
                        last_name="Testuser", image_url="http://ficticiouswebsite.com/rot.jpg")
        db.session.add(new_user)
        db.session.commit()

        self.user_id = new_user.id
        self.user = new_user

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            # a redirect will occur to /users
            resp = client.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"{self.user.first_name} {self.user.last_name}", html)
            self.assertIn('Add User', html)

    def test_view_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"{self.user.first_name} {self.user.last_name}", html)
            self.assertIn(self.user.image_url, html)

            self.assertIn('Edit</button>', html)
            self.assertIn('"Delete"', html)
            self.assertNotIn('disabled value="Delete"', html)
            self.assertIn('Add Post', html)
            # 'Posts' text only appears when user has posts
            self.assertNotIn('Posts</span>', html)

    def test_edit_user(self):
        with app.test_client() as client:
            # Even though it is an edit, the form has viewable elements
            #  about user.
            resp = client.get(f"/users/{self.user_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('name="first-name"', html)
            self.assertIn(self.user.first_name, html)
            self.assertIn('name="last-name"', html)
            self.assertIn(self.user.last_name, html)
            self.assertIn('name="image-url"', html)
            self.assertIn(self.user.image_url, html)

            self.assertIn('Save', html)
            self.assertIn('Cancel', html)

    def test_delete_user_process(self):
        with app.test_client() as client:
            # Test the delete. We should redirect to an empty
            # users list.
            resp = client.post(
                f"/users/{self.user_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Blogly Users</h1>', html)
            self.assertIn('Add User', html)
            self.assertNotIn(
                f"{self.user.first_name} {self.user.last_name}", html)


class BloglyPostTests(TestCase):
    """Tests for Blogly Post add, view, and edit functions."""

    @classmethod
    def setUpClass(cls):
        """Add blogly user and post."""

        db.session.rollback()

        Post.query.delete()
        db.session.commit()
        User.query.delete()
        db.session.commit()

        new_user = User(first_name="Eric",
                        last_name="Cartman", image_url="http://ficticiouswebsite.com/namtraccire.jpg")

        db.session.add(new_user)
        db.session.commit()

        new_post = Post(title="Screw You Guys. . .", content=". . . I am going home!",
                        created_at="2021-03-09 16:00", user_id=1)
        db.session.add(new_post)
        db.session.commit()

    def setUp(self):
        """Add blogly user and post."""

        self.user_id = 1

        self.user = User.query.get(self.user_id)

        self.post_id = self.user.posts[0].user_id
        self.post = Post.query.get(self.post_id)

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_view_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f'{self.user.first_name} {self.user.last_name}', html)
            self.assertIn(self.user.image_url, html)

            self.assertIn('Edit</button>', html)
            self.assertIn('disabled value="Delete"', html)
            self.assertIn('Add Post', html)
            # 'Posts' text only appears when user has posts
            self.assertIn('Posts</span>', html)
            self.assertIn(self.post.title, html)

    def test_view_post(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.post.title, html)
            self.assertIn(self.post.content, html)
            self.assertIn('by Eric Cartman', html)
            # verify leading zero removed from day and time
            self.assertIn('Tue Mar 9, 2021 4:00 PM', html)

            self.assertIn('Edit</button>', html)
            self.assertIn('Delete', html)

    def test_edit_post(self):
        with app.test_client() as client:
            # Even though it is an edit, the form has viewable post elements
            resp = client.get(f"/posts/{self.post_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('name="post-title"', html)
            self.assertIn(self.post.title, html)
            self.assertIn('name="post-content"', html)
            self.assertIn(self.post.content, html)

            self.assertIn('Save', html)
            self.assertIn('Cancel', html)


class BloglyPostTests(TestCase):
    """Tests for Blogly Post delete function."""

    @classmethod
    def setUpClass(cls):
        """Add blogly user and post."""

        db.session.rollback()

        Post.query.delete()
        db.session.commit()
        User.query.delete()
        db.session.commit()

        new_user = User(first_name="Eric",
                        last_name="Cartman", image_url="http://ficticiouswebsite.com/namtraccire.jpg")

        db.session.add(new_user)
        db.session.commit()

        new_post = Post(title="3 Js", content="Jersey, Jinja. . . ",
                        created_at="2021-03-09 16:00", user_id=1)
        db.session.add(new_post)
        db.session.commit()

    def setUp(self):
        """Add blogly user and post."""

        self.user_id = 1

        self.user = User.query.get(self.user_id)

        self.post_id = self.user.posts[0].user_id
        self.post = Post.query.get(self.post_id)

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    # there should be a test to ensure a user cannot get delete when they is a post
    #  attached.

    # zero idea why the post delete could not happen with all the other tests.
    def test_delete_post_process(self):
        with app.test_client() as client:
            # Test the delete. We should redirect to an empty posts list for the user
            resp = client.post(
                f"/posts/{self.post_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Blogly User</h1>', html)
            self.assertIn("Cartman", html)
            self.assertIn('Add Post', html)
            self.assertNotIn("3 Js", html)
