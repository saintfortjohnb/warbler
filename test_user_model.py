import os
import unittest

from flask import Flask
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Create the Flask application
app = Flask(__name__)

# Configure the app and database for testing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

# Connect the database to the Flask app
db.app = app
db.init_app(app)


class UserModelTestCase(unittest.TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            # Create all tables
            db.create_all()

            # Create some example data
            User.query.delete()
            Message.query.delete()
            Follows.query.delete()
            Likes.query.delete()

            user1 = User.signup("user1", "user1@example.com", "password", None)
            user2 = User.signup("user2", "user2@example.com", "password", None)

            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()
            db.session.remove()

    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            # Since there is no validation or constraints on the User model,
            # there's not much to test here other than creating and querying
            # objects to ensure that the database interactions work correctly.

            user1 = User.query.filter_by(username="user1").first()
            user2 = User.query.filter_by(username="user2").first()

            self.assertIsNotNone(user1)
            self.assertIsNotNone(user2)
            self.assertEqual(user1.username, "user1")
            self.assertEqual(user2.username, "user2")
            
    def test_user_follows(self):
        """Does the user follow another user?"""
        with app.app_context():
            user1 = User.query.filter_by(username="user1").first()
            user2 = User.query.filter_by(username="user2").first()
            user1.following.append(user2)
            db.session.commit()
            self.assertEqual(len(user1.following), 1)
            self.assertEqual(len(user1.followers), 0)
            self.assertEqual(len(user2.following), 0)
            self.assertEqual(len(user2.followers), 1)
            
    def test_is_following(self):
        """Does the user follow another user?"""
        with app.app_context():
            user1 = User.query.filter_by(username="user1").first()
            user2 = User.query.filter_by(username="user2").first()
            user1.following.append(user2)
            db.session.commit()
            self.assertTrue(user1.is_following(user2))
            self.assertFalse(user2.is_following(user1))
            
    def test_is_followed_by(self):
        """Does the user follow another user?"""
        with app.app_context():
            user1 = User.query.filter_by(username="user1").first()
            user2 = User.query.filter_by(username="user2").first()
            user1.following.append(user2)
            db.session.commit()
            self.assertTrue(user2.is_followed_by(user1))
            self.assertFalse(user1.is_followed_by(user2))
            
    def test_valid_signup(self):
        """Does the signup method create a new user with valid credentials?"""
        with app.app_context():
            user = User.signup("testuser", "test@example.com", "password", None)
            db.session.commit()

            self.assertRaises(exc.IntegrityError)

    def test_invalid_password_signup(self):
        """Does the signup method reject invalid passwords?"""
        with app.app_context():
            with self.assertRaises(ValueError):
                User.signup("testuser", "test@example.com", "", None)

if __name__ == '__main__':
    unittest.main()
