from datetime import datetime, timedelta
from database.db import get_session
from models.subscription import Subscription
from models.user import User


class SubscriptionService:

    @staticmethod
    def activate_premium(user_id, days=30):
        session = get_session()
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if user:
            user.is_premium = True
            user.premium_until = datetime.utcnow() + timedelta(days=days)
            session.commit()
            return True

        return False

    @staticmethod
    def get_subscription_info(user_id):
        session = get_session()
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if user and user.is_premium:
            return {
                'active': True,
                'until': user.premium_until.strftime('%d.%m.%Y')
            }

        return {'active': False}