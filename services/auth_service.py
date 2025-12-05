from database.db import get_session
from models.user import User
from datetime import datetime


class AuthService:

    @staticmethod
    def get_or_create_user(telegram_id, username, first_name):
        session = get_session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name
            )
            session.add(user)
            session.commit()

        return user

    @staticmethod
    def check_premium_status(user_id):
        session = get_session()
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if user and user.is_premium:
            if user.premium_until > datetime.utcnow():
                return True
            else:
                user.is_premium = False
                session.commit()

        return False