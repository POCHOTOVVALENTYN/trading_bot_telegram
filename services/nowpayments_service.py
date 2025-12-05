import requests
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import (
    NOWPAYMENTS_API_KEY, NOWPAYMENTS_IPN_KEY,
    NOWPAYMENTS_API_URL, NOWPAYMENTS_EMAIL, TARIFFS
)
from database.db import get_session
from models.subscription import Subscription


class NOWPaymentsService:
    """Сервис для работы с NOWPayments"""

    def __init__(self):
        self.api_key = NOWPAYMENTS_API_KEY
        self.ipn_key = NOWPAYMENTS_IPN_KEY
        self.api_url = NOWPAYMENTS_API_URL
        self.merchant_email = NOWPAYMENTS_EMAIL

    def create_payment(
            self,
            user_id: int,
            tariff: str,
            currency: str = "usdttrx"  # USDT на Tron
    ) -> Dict:
        """
        Создает платеж через NOWPayments

        Поддерживаемые валюты:
        - usdterc20 (Ethereum)
        - usdttrx (Tron) - РЕКОМЕНДУЕТСЯ
        - usdt_ton (TON)
        """

        if tariff not in TARIFFS:
            return {"success": False, "error": "Unknown tariff"}

        tariff_info = TARIFFS[tariff]
        amount = tariff_info['price_usdt']

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        import time
        payload = {
            "price_amount": amount,
            "price_currency": "usd",
            "pay_currency": currency,
            "order_id": f"user_{user_id}_{int(time.time())}",
            "order_description": f"{tariff_info['name']} подписка",
            "ipn_callback_url": "https://your-domain.com/webhooks/nowpayments",
            "success_url": "https://your-domain.com/payment/success",
            "cancel_url": "https://your-domain.com/payment/cancel"
        }

        try:
            response = requests.post(
                f"{self.api_url}/invoice",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 201:
                data = response.json()

                session = get_session()
                subscription = Subscription(
                    user_id=user_id,
                    payment_id=data.get("id"),
                    payment_method='nowpayments',
                    amount=amount,
                    currency='USDT',
                    tariff=tariff,
                    status='pending',
                    nowpayments_id=data.get("invoice_id"),
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                session.add(subscription)
                session.commit()

                return {
                    "success": True,
                    "payment_url": data.get("invoice_url"),
                    "payment_id": data.get("id"),
                    "amount": amount,
                    "tariff": tariff,
                    "tariff_name": tariff_info['name']
                }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": "Unknown error"}

    def verify_ipn(self, request_data: Dict, signature: str) -> bool:
        """Проверяет подпись IPN callback"""

        sorted_data = sorted(request_data.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_data if k != "v"])

        expected_signature = hmac.new(
            self.ipn_key.encode(),
            param_string.encode(),
            hashlib.sha512
        ).hexdigest()

        return signature == expected_signature

    def confirm_payment(self, payment_id: str, days: int = 30) -> bool:
        """Подтверждает платеж"""

        session = get_session()
        subscription = session.query(Subscription).filter_by(
            payment_id=payment_id
        ).first()

        if not subscription:
            return False

        try:
            subscription.status = 'completed'
            subscription.completed_at = datetime.utcnow()
            session.commit()

            from services.subscription_service import SubscriptionService
            SubscriptionService.activate_premium(subscription.user_id, days)

            return True

        except Exception as e:
            print(f"Error: {e}")
            return False


nowpayments_service = NOWPaymentsService()
