import os
import requests
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio
from config import (
    TON_RPC_URL, TONCENTER_API_KEY, TON_MERCHANT_ADDRESS,
    TON_USDT_ADDRESS, TARIFFS
)
from database.db import get_session
from models.subscription import Subscription


class TONPaymentService:
    """Сервис для работы с USDT на TON блокчейне"""

    def __init__(self):
        self.ton_rpc = TON_RPC_URL
        self.api_key = TONCENTER_API_KEY
        self.merchant_address = TON_MERCHANT_ADDRESS
        self.usdt_master_address = TON_USDT_ADDRESS

    def create_invoice(
            self,
            user_id: int,
            tariff: str,
            description: str = "Premium подписка"
    ) -> Dict:
        """
        Создает счет для пользователя

        Args:
            user_id: Telegram ID пользователя
            tariff: Код тарифа (basic, pro, vip)
            description: Описание платежа

        Returns:
            Словарь с информацией о платеже
        """

        if tariff not in TARIFFS:
            return {"success": False, "error": "Unknown tariff"}

        tariff_info = TARIFFS[tariff]
        amount = tariff_info['price_usdt']

        # Генерируем уникальный ID платежа
        payment_id = f"ton_{user_id}_{int(datetime.utcnow().timestamp())}"

        # Сохраняем в БД
        session = get_session()
        subscription = Subscription(
            user_id=user_id,
            payment_id=payment_id,
            payment_method='ton',
            amount=amount,
            currency='USDT',
            tariff=tariff,
            status='pending',
            wallet_address=self.merchant_address,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            payment_metadata='{"description": "'
                             + description + '", "created_at": "' + datetime.utcnow().isoformat() + '"}'
        )
        session.add(subscription)
        session.commit()

        return {
            "success": True,
            "payment_id": payment_id,
            "address": self.merchant_address,
            "amount": amount,
            "amount_nanotons": int(amount * 1e6),
            "currency": "USDT",
            "tariff": tariff,
            "tariff_name": tariff_info['name'],
            "expires_at": subscription.expires_at.isoformat()
        }

    def get_payment_link(
            self,
            address: str,
            amount: float,
            comment: str = ""
    ) -> str:
        """
        Генерирует ссылку для платежа через TON

        Формат: ton://transfer/[address]?amount=[amount]&text=[comment]
        """

        # Конвертируем USDT в nanotons
        amount_nanotons = int(amount * 1e6)

        # Генерируем ссылку
        link = f"ton://transfer/{address}?amount={amount_nanotons}&text={comment}"

        return link

    async def check_payment(
            self,
            payment_id: str,
            expected_amount: float,
            timeout: int = 600
    ) -> Dict:
        """
        Проверяет поступление платежа

        Args:
            payment_id: ID платежа
            expected_amount: Ожидаемая сумма в USDT
            timeout: Таймаут проверки в секундах

        Returns:
            Статус платежа
        """

        session = get_session()
        subscription = session.query(Subscription).filter_by(
            payment_id=payment_id
        ).first()

        if not subscription:
            return {"success": False, "status": "not_found"}

        start_time = datetime.utcnow()
        # Получаем комментарий, который мы ожидаем увидеть в транзакции
        # Формат комментария был задан в create_invoice: "Subscribe_{tariff}"?
        # В handle_ton_payment вы передали comment=f"Subscribe_{tariff}" в ссылку,
        # но для проверки нужно точно знать, что искать.
        # Лучше искать по уникальному ID платежа, если бы вы просили пользователя его указать.
        # Но так как вы просите указать tariff, будем искать входящую транзакцию с нужной суммой.
        expected_nanotons = int(expected_amount * 1e6)
        while True:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout:
                return {
                    "success": False,
                    "status": "timeout",
                    "message": "Время ожидания платежа истекло"
                }

            try:
                # Используем метод getTransactions (последние транзакции)
                url = f"{self.ton_rpc}/getTransactions"
                params = {
                    "address": self.merchant_address,
                    "limit": 10,  # Проверяем последние 10 транзакций
                    "archival": "true"
                }
                headers = {"X-API-Key": self.api_key}

                response = requests.get(url, params=params, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        transactions = data.get("result", [])
                        for tx in transactions:
                            # Проверяем входящие сообщения (in_msg)
                            in_msg = tx.get("in_msg", {})

                            # Проверяем value (сумма)
                            value = int(in_msg.get("value", 0))

                            # Важно: проверить время транзакции (utime), чтобы не засчитать старые
                            tx_time = tx.get("utime", 0)
                            if tx_time < subscription.created_at.timestamp():
                                continue

                            # Если сумма совпадает (с небольшой погрешностью или точно)
                            if value == expected_nanotons:
                                return {
                                    "success": True,
                                    "status": "completed",
                                    "message": "Платеж найден!"
                                }
            except Exception as e:
                print(f"TON check error: {e}")

            await asyncio.sleep(10)  # Пауза перед следующей проверкой

    def confirm_payment(self, payment_id: str, days: int = 30) -> bool:
        """
        Подтверждает платеж и активирует подписку
        """

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

            # Активируем подписку
            from services.subscription_service import SubscriptionService
            SubscriptionService.activate_premium(subscription.user_id, days)

            return True

        except Exception as e:
            print(f"Error confirming payment: {e}")
            return False


# Инициализация
ton_service = TONPaymentService()