from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.ton_payment_service import ton_service
from config import TARIFFS
import asyncio


async def handle_ton_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка платежа через TON"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Извлекаем тариф из callback_data (pay_ton_basic -> basic)
    tariff = query.data.split('_')[-1]

    # Создаем счет
    invoice = ton_service.create_invoice(
        user_id=user_id,
        tariff=tariff,
        description=f"Premium {tariff} подписка"
    )

    if not invoice.get("success"):
        await query.edit_message_text("❌ Ошибка при создании платежа")
        return

    # Генерируем ссылку для платежа
    payment_link = ton_service.get_payment_link(
        address=invoice["address"],
        amount=invoice["amount"],
        comment=f"Subscribe_{tariff}"
    )

    # Форматируем текст платежа
    payment_text = f"""
✅ **ПЛАТЕЖ ГОТОВ К ОТПРАВКЕ**

Тариф: *{invoice['tariff_name']}*
Сумма: *${invoice['amount']} USDT (TON)*

📍 Адрес: `{invoice['address']}`

**Способы оплаты:**

1️⃣ *Через Telegram Wallet (Рекомендуется)*
   Нажмите кнопку "💳 Оплатить" ниже

2️⃣ *Через другой кошелек*
   Скопируйте адрес выше и отправьте {invoice['amount']} USDT на этот адрес

⏳ Время на оплату: *1 час*
    """

    buttons = [
        [InlineKeyboardButton("💳 Оплатить через Telegram", url=payment_link)],
        [InlineKeyboardButton("✅ Я отправил платеж", callback_data=f"ton_confirm_{invoice['payment_id']}")],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        payment_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    # Сохраняем информацию в контекст
    context.user_data['pending_payment'] = invoice


async def handle_ton_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия 'Я отправил платеж'"""
    query = update.callback_query
    await query.answer()

    # Извлекаем payment_id
    payment_id = query.data.split('_')[-1]

    checking_text = """
⏳ **ПРОВЕРЯЮ БЛОКЧЕЙН...**

Это может занять 1-3 минуты.
    """

    await query.edit_message_text(checking_text, parse_mode='Markdown')

    # Проверяем платеж
    result = await ton_service.check_payment(
        payment_id=payment_id,
        expected_amount=context.user_data.get('pending_payment', {}).get('amount', 0),
        timeout=300  # 5 минут
    )

    if result.get("success") and result.get("status") == "completed":
        # Активируем подписку
        ton_service.confirm_payment(payment_id, days=30)

        success_text = """
✅ **ПЛАТЕЖ ПОЛУЧЕН!**

Ваша подписка активирована на 30 дней.

Теперь у вас есть доступ ко всем Premium-функциям:
- 🤖 AI-аналитик
- 🚀 Торговые сигналы
- 📊 Премиум-аналитика
- 🎓 Обучающий курс

Спасибо за покупку! 🎉
        """

        buttons = [
            [InlineKeyboardButton("🤖 Начать с AI-чата", callback_data="ai_chat")],
            [InlineKeyboardButton("📊 Premium меню", callback_data="premium_menu")]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            success_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        pending_text = """
⏳ **ПЛАТЕЖ ЕЩЕ НЕ НАЙДЕН**

Это может быть потому что:
- Платеж еще обрабатывается (обычно 1-3 мин)
- Платеж был отправлен на неправильный адрес
- Сумма не совпадает

**Что делать:**
1. Проверьте адрес и сумму
2. Подождите 2-3 минуты
3. Нажмите кнопку "Проверить еще раз"

Если проблема сохранится - обратитесь в поддержку.
        """

        buttons = [
            [InlineKeyboardButton("🔄 Проверить еще раз", callback_data=f"ton_confirm_{payment_id}")],
            [InlineKeyboardButton("📞 Поддержка", callback_data="support")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            pending_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )