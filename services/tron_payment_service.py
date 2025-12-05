import os
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta
from config import (
    TRON_RPC_URL, TRON_MERCHANT_ADDRESS, TRON_PRIVATE_KEY,
    TRON_USDT_CONTRACT, TRON_USDT_DECIMALS, TARIFFS
)
from database.db import get_session
from models.subscription import Subscription

try:
    from tronpy import Tron
    from tronpy.exceptions import TransactionNotFound

    TRONPY_AVAILABLE = True
except ImportError:
    TRONPY_AVAILABLE = False
    print("⚠️ tronpy не установлен. Установите: pip install tronpy")


class TronUSDTService:
    """Сервис для приема USDT TRC20 платежей на Tron"""

    def __init__(self):
        if TRONPY_AVAILABLE:
            self.tron = Tron(provider=TRON_RPC_URL)
        else:
            self.tron = None

        self.merchant_address = TRON_MERCHANT_ADDRESS
        self.merchant_private_key = TRON_PRIVATE_KEY
        self.usdt_contract = TRON_USDT_CONTRACT
        self.decimals = TRON_USDT_DECIMALS

    def create_invoice(
            self,
            user_id: int,
            tariff: str,
            description: str = "Premium подписка"
    ) -> Dict:
        """
        Создает счет для пользователя
        """

        if tariff not in TARIFFS:
            return {"success": False, "error": "Unknown tariff"}

        tariff_info = TARIFFS[tariff]
        amount = tariff_info['price_usdt']

        payment_id = f"tron_{user_id}_{int(datetime.utcnow().timestamp())}"

        # Сохраняем в БД
        session = get_session()
        subscription = Subscription(
            user_id=user_id,
            payment_id=payment_id,
            payment_method='tron_usdt',
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
            "amount_sun": int(amount * (10 ** self.decimals)),
            "currency": "USDT TRC20",
            "tariff": tariff,
            "tariff_name": tariff_info['name'],
            "expires_at": subscription.expires_at.isoformat(),
            "explorer_url": f"https://tronscan.org/#/address/{self.merchant_address}"
        }

    def get_tron_address_url(self, address: str) -> str:
        """Получить URL адреса на Tronscan"""
        return f"https://tronscan.org/#/address/{address}"

    async def check_payment(
            self,
            payment_id: str,
            expected_amount_sun: int,
            timeout: int = 600
    ) -> Dict:
        """
        Проверяет поступление платежа на адрес

        Args:
            payment_id: ID платежа
            expected_amount_sun: Ожидаемая сумма в sun (1 USDT = 1e6)
            timeout: Таймаут в секундах

        Returns:
            Статус платежа
        """

        if not self.tron:
            return {"success": False, "error": "Tron service not available"}

        start_time = datetime.utcnow()
        check_count = 0
        max_checks = 60  # 60 проверок

        while check_count < max_checks:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > timeout:
                return {
                    "success": False,
                    "status": "timeout",
                    "message": "Время ожидания платежа истекло"
                }

            try:
                # Получаем последние транзакции
                transactions = self.tron.get_address_transactions(self.merchant_address)

                if not transactions or not transactions.get("data"):
                    await asyncio.sleep(10)
                    check_count += 1
                    continue

                # Проверяем каждую транзакцию
                for tx in transactions.get("data", []):
                    tx_hash = tx.get("txID")

                    if self._is_usdt_transfer(tx, expected_amount_sun):
                        return {
                            "success": True,
                            "status": "completed",
                            "tx_hash": tx_hash,
                            "amount": expected_amount_sun,
                            "explorer_url": f"https://tronscan.org/#/transaction/{tx_hash}"
                        }

            except Exception as e:
                print(f"Tron check error: {e}")

            # Ждем 10 секунд перед следующей проверкой
            await asyncio.sleep(10)
            check_count += 1

        return {
            "success": False,
            "status": "timeout",
            "message": "Платеж не найден за отведенное время"
        }

    def _is_usdt_transfer(self, tx: Dict, expected_amount: int) -> bool:
        """
        Проверяет является ли транзакция переводом USDT
        """

        try:
            # 1. Проверяем, что контракт вызван успешно
            if tx.get("ret", [{}])[0].get("contractRet") != "SUCCESS":
                return False

            raw_data = tx.get("raw_data", {}).get("contract", [{}])[0]
            parameter = raw_data.get("parameter", {}).get("value", {})

            # 2. Проверяем, что это вызов USDT контракта
            contract_address = parameter.get("contract_address")
            # Конвертируем адрес из hex если нужно, или сравниваем с конфигом
            # (TronGrid возвращает адреса в разном формате, часто Base58Check)

            # 3. Декодируем данные (input data)
            # В поле 'data' лежит вызов функции transfer(to, amount)
            # Это сложная часть без web3 библиотек.

            # УПРОЩЕННОЕ РЕШЕНИЕ ДЛЯ TRONPY (если она установлена):
            # Если вы используете self.tron.get_transaction(tx_hash),
            # библиотека может сама распарсить поля.

            # Если вы используете HTTP API вручную, вам нужно проверить:
            # - Функция: a9059cbb (transfer)
            # - Сумма: последние 64 символа hex строки data -> перевести в int

            # ВРЕМЕННОЕ РЕШЕНИЕ (на основе суммы перевода TRX, если это не токен):
            # Внимание: для USDT TRC20 этот метод _обязан_ парсить data.
            # Если вы не можете реализовать парсинг data сейчас, бот не сможет надежно проверять USDT.

            return False  # Пока возвращаем False, чтобы не подтверждать все подряд.

        except Exception:
            return False

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
tron_service = TronUSDTService()