import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.start_handler import start_handler
from handlers.crypto_payment_handler import (
    handle_buy_premium, handle_choose_tariff
)
from handlers.ton_payment_handler import (
    handle_ton_payment, handle_ton_confirm
)
from handlers.tron_payment_handler import (
    handle_tron_payment, handle_tron_confirm
)
from handlers.nowpayments_handler import (
    handle_nowpayments_payment, handle_nowpayments_confirm
)
from database.db import init_db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main():
    # Инициализация БД
    init_db()

    # Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # ========== ОСНОВНЫЕ КОМАНДЫ ==========
    app.add_handler(CommandHandler("start", start_handler))

    # ========== ПЛАТЕЖИ: ВЫБОР МЕТОДА ==========
    app.add_handler(CallbackQueryHandler(handle_buy_premium, pattern="^buy_premium$"))
    app.add_handler(CallbackQueryHandler(handle_choose_tariff, pattern="^payment_method_"))

    # ========== ПЛАТЕЖИ: TON ==========
    app.add_handler(CallbackQueryHandler(handle_ton_payment, pattern="^pay_ton_"))
    app.add_handler(CallbackQueryHandler(handle_ton_confirm, pattern="^ton_confirm_"))

    # ========== ПЛАТЕЖИ: TRON ==========
    app.add_handler(CallbackQueryHandler(handle_tron_payment, pattern="^pay_tron_"))
    app.add_handler(CallbackQueryHandler(handle_tron_confirm, pattern="^tron_confirm_"))

    # ========== ПЛАТЕЖИ: NOWPAYMENTS ==========
    app.add_handler(CallbackQueryHandler(handle_nowpayments_payment, pattern="^pay_now_"))
    app.add_handler(CallbackQueryHandler(handle_nowpayments_confirm, pattern="^now_confirm_"))

    print("✅ Бот запущен с поддержкой крипто-платежей!")
    print("   🌐 TON Wallet")
    print("   🔗 USDT TRC20")
    print("   🌍 NOWPayments")

    app.run_polling()


if __name__ == "__main__":
    main()