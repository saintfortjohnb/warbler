import os
from unittest import TestCase
import unittest

from models import db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser", email="test@test.com", password="testuser", image_url=None)
            self.testuser_id = 8989
            self.testuser.id = self.testuser_id

            db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    user = User.query.get(self.testuser_id)
                    sess[CURR_USER_KEY] = user.id
                    self.testuser = user
        
                resp = c.post("/messages/new", data={"text": "Hello"})

                self.assertEqual(resp.status_code, 302)

                msg = Message.query.one()
                self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224 # user does not exist

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def setup_message(self):
        with app.app_context():
            m = Message(
                id=1234,
                text="a test message",
                user_id=self.testuser_id
            )

            db.session.add(m)
            db.session.commit()

    def test_message_show(self):
        self.setup_message()
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    user = User.query.get(self.testuser_id)
                    sess[CURR_USER_KEY] = user.id
                    self.testuser = user
                
                m = Message.query.get(1234)

                resp = c.get(f'/messages/{m.id}')

                self.assertEqual(resp.status_code, 200)
                self.assertIn(m.text, str(resp.data))

    def test_message_delete(self):
        self.setup_message()

        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    user = User.query.get(self.testuser_id)
                    sess[CURR_USER_KEY] = user.id
                    self.testuser = user

                resp = c.post("/messages/1234/delete", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                m = Message.query.get(1234)
                self.assertIsNone(m)

    def test_unauthorized_message_delete(self):
        with app.app_context():
            # A second user that will try to delete the message
            u = User.signup(username="unauthorized-user",
                            email="testtest@test.com",
                            password="password",
                            image_url=None)
            u.id = 76543

        self.setup_message()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):
        self.setup_message()

        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)
            
    def test_invalid_message_show(self):
        with app.app_context():
            with self.client as c:
                with c.session_transaction() as sess:
                    user = User.query.get(self.testuser_id)
                    sess[CURR_USER_KEY] = user.id
                    self.testuser = user
                
                resp = c.get('/messages/99999999')

                self.assertEqual(resp.status_code, 500)

if __name__ == '__main__':
    unittest.main()