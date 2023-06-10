import os
import unittest

from flask import Flask

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.app = app
db.init_app(app)

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            db.create_all()

            User.query.delete()
            Message.query.delete()
            Follows.query.delete()
            Likes.query.delete()

            self.user1 = User.signup("user1", "user1@example.com", "password", None)
            self.user2 = User.signup("user2", "user2@example.com", "password", None)

            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()
            db.session.remove()

    def test_message_model(self):
        with app.app_context():
            user1 = User.query.filter_by(username="user1").first()
            message = Message(text='Test message', user_id=user1.id)
            db.session.add(message)
            db.session.commit()
            self.assertEqual(message.text, 'Test message')
            self.assertEqual(message.user_id, user1.id)
            self.assertEqual(len(user1.messages), 1)

    def test_message_likes(self):
        with app.app_context():
            user1 = User.query.filter_by(username="user1").first()
            message1 = Message(text='Test message', user_id=user1.id)
            message2 = Message(text='warble, interesting', user_id=user1.id)
            db.session.add_all([message1, message2])
            db.session.commit()
            
            user2 = User.query.filter_by(username="user2").first()
            user2.likes.append(message1)
            db.session.commit()
            
            like1 = Likes.query.filter(Likes.user_id == user2.id).all()
            self.assertEqual(len(like1), 1)
            self.assertEqual(like1[0].message_id, message1.id)

if __name__ == '__main__':
    unittest.main()
