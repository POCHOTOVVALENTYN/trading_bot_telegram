from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.tron_payment_service import tron_service
import asyncio


async def handle_tron_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка платежа через USDT TRC20"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    tariff = query.data.split('_')[-1]  # pay_tron_basic -> basic

    # Создаем счет
    invoice = tron_service.create_invoice(
        user_id=user_id,
        tariff=tariff
    )

    if not invoice.get("success"):
        await query.edit_message_text("❌ Ошибка при создании платежа")
        return

    payment_text = f"""
✅ **ПЛАТЕЖ ГОТОВ К ОТПРАВКЕ**

Тариф: *{invoice['tariff_name']}*
Сумма: *${invoice['amount']} USDT (TRC20)*

📍 Адрес кошелька:
`{invoice['address']}`

⛓️ Сеть: *Tron (TRC20)*

**Инструкция:**

1️⃣ Скопируйте адрес выше
2️⃣ Откройте свой крипто-кошелек (Tronkeeper, Ledger, Binance и т.д.)
3️⃣ Отправьте точно *{invoice['amount']} USDT TRC20* на этот адрес
4️⃣ Нажмите "Я отправил платеж"

📍 Проверить статус: {invoice['explorer_url']}

⏳ Время на оплату: *1 час*
    """

    buttons = [
        [InlineKeyboardButton("📋 Скопировать адрес", callback_data=f"copy_addr_{invoice['payment_id']}")],
        [InlineKeyboardButton("✅ Я отправил платеж", callback_data=f"tron_confirm_{invoice['payment_id']}")],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        payment_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    context.user_data['pending_payment'] = invoice


async def handle_tron_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка платежа Tron"""
    query = update.callback_query
    await query.answer()

    payment_id = query.data.split('_')[-1]
    pending = context.user_data.get('pending_payment', {})

    await query.edit_message_text(
        "⏳ Проверяю блокчейн Tron...\n\nЭто может занять 1-2 минуты.",
        parse_mode='Markdown'
    )

    result = await tron_service.check_payment(
        payment_id=payment_id,
        expected_amount_sun=pending.get('amount_sun', 0),
        timeout=300
    )

    if result.get("success"):
        tron_service.confirm_payment(payment_id, days=30)

        success_text = f"""
✅ **ПЛАТЕЖ ПОЛУЧЕН!**

TX: `{result.get('tx_hash', 'N/A')}`

Ваша подписка активирована на 30 дней.

Спасибо за покупку! 🎉
        """

        buttons = [
            [InlineKeyboardButton("🤖 AI-чат", callback_data="ai_chat")],
            [InlineKeyboardButton("📊 Premium меню", callback_data="premium_menu")]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            success_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "⏳ Платеж еще не найден.\n\nПопробуйте еще раз через 30 сек или проверьте адрес.",
            parse_mode='Markdown'
        )
