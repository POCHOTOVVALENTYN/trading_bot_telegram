

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # telegram_id
    payment_id = Column(String, unique=True, nullable=False)

    # Платежные методы
    payment_method = Column(String)  # 'ton', 'tron_usdt', 'nowpayments', 'liqpay'

    # Информация о платеже
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USDT")  # USDT, TON, USD
    tariff = Column(String)
    status = Column(String, default="pending")  # pending, completed, failed, expired

    # Данные блокчейна
    wallet_address = Column(String)  # Адрес кошелька для отправки
    blockchain_tx_hash = Column(String)  # TX hash блокчейна
    blockchain_confirmations = Column(Integer, default=0)

    # Внешние ID (для разных провайдеров)
    liqpay_id = Column(String)
    nowpayments_id = Column(String)
    tron_explorer_link = Column(String)

    # ⬇️ ИСПРАВЛЕНО: Переименовано с 'metadata' на 'payment_metadata'
    # SQLAlchemy использует 'metadata' внутри, поэтому это зарезервированное имя
    payment_metadata = Column(Text)  # JSON строка с дополнительными данными

    # Времена
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Subscription user={self.user_id} method={self.payment_method} status={self.status}>"


# ============================================
# Также обновить в models/user.py (если используется)
# ============================================

class User(Base):
    __tablename__ = 'users'

    from sqlalchemy import Column, Integer, String, DateTime, Boolean

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User telegram_id={self.telegram_id} username={self.username}>"