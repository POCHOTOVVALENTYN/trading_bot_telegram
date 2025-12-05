import os
from dotenv import load_dotenv

load_dotenv()

# ========== ОСНОВНОЕ ==========
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
APP_ENV = os.getenv('APP_ENV', 'development')

# ========== ТАРИФЫ ==========
TARIFFS = {
    'basic': {
        'name': 'Базовый',
        'price_usd': 2.99,
        'price_usdt': 2.99,
        'duration_days': 30,
        'features': ['AI Аналитик (40 вопросов)', '5 сигналов']
    },
    'pro': {
        'name': 'Pro',
        'price_usd': 9.99,
        'price_usdt': 9.99,
        'duration_days': 30,
        'features': ['AI Аналитик (200 вопросов)', 'Канал сигналов', 'Аналитика']
    },
    'vip': {
        'name': 'VIP',
        'price_usd': 29.99,
        'price_usdt': 29.99,
        'duration_days': 30,
        'features': ['Безлимит AI', 'Приоритетная поддержка', 'Авторские рекомендации']
    }
}

# ========== TON WALLET (Вариант 1) ==========
TON_ENABLED = True
TON_RPC_URL = os.getenv('TON_RPC_URL')
TONCENTER_API_KEY = os.getenv('TONCENTER_API_KEY')
TON_MERCHANT_ADDRESS = os.getenv('TON_MERCHANT_ADDRESS')
TON_USDT_ADDRESS = "EQCxE6mUtQJKjI05zW67G44xLcnSW_QfMh2IWhAH0vHqMNwt"

# ========== USDT TRC20 / TRON (Вариант 2) ==========
TRON_ENABLED = True
TRON_RPC_URL = os.getenv('TRON_RPC_URL')
TRON_MERCHANT_ADDRESS = os.getenv('TRON_MERCHANT_ADDRESS')
TRON_PRIVATE_KEY = os.getenv('TRON_PRIVATE_KEY')
TRON_USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
TRON_USDT_DECIMALS = 6

# ========== NOWPAYMENTS (Вариант 3) ==========
NOWPAYMENTS_ENABLED = True
NOWPAYMENTS_API_KEY = os.getenv('NOWPAYMENTS_API_KEY')
NOWPAYMENTS_IPN_KEY = os.getenv('NOWPAYMENTS_IPN_KEY')
NOWPAYMENTS_EMAIL = os.getenv('NOWPAYMENTS_EMAIL')
NOWPAYMENTS_API_URL = "https://api.nowpayments.io/v1"

# ========== ПЛАТЕЖНЫЕ МЕТОДЫ ==========
PAYMENT_METHODS = {
    'ton': {
        'name': 'TON Wallet',
        'enabled': TON_ENABLED,
        'icon': '🌐',
        'description': 'Встроена в Telegram. Комиссия 0.1-0.5%. Скорость 1-3 сек'
    },
    'tron_usdt': {
        'name': 'USDT TRC20',
        'enabled': TRON_ENABLED,
        'icon': '🔗',
        'description': 'USDT на Tron. Комиссия $0.1-1. Скорость 1-2 мин'
    },
    'nowpayments': {
        'name': 'NOWPayments',
        'enabled': NOWPAYMENTS_ENABLED,
        'icon': '🌍',
        'description': '100+ криптовалют. Комиссия 0.5-1%. Скорость 5-30 мин'
    }
}