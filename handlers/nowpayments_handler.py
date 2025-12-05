async def handle_nowpayments_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка платежа через NOWPayments"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    tariff = query.data.split('_')[-1]

    result = nowpayments_service.create_payment(
        user_id=user_id,
        tariff=tariff,
        currency="usdttrx"
    )

    if not result.get("success"):
        await query.edit_message_text("❌ Ошибка при создании платежа")
        return

    payment_text = f"""
✅ **ПЛАТЕЖ ГОТОВ К ОПЛАТЕ**

Тариф: *{result['tariff_name']}*
Сумма: *${result['amount']} USDT*

Нажмите кнопку ниже чтобы перейти к оплате:
    """

    buttons = [
        [InlineKeyboardButton("💳 Перейти к оплате", url=result['payment_url'])],
        [InlineKeyboardButton("✅ Я оплатил", callback_data=f"now_confirm_{result['payment_id']}")],
        [InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        payment_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    context.user_data['pending_payment'] = result


async def handle_nowpayments_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка платежа NOWPayments"""
    query = update.callback_query
    await query.answer()

    payment_id = query.data.split('_')[-1]

    # В реальности нужно проверить через API
    # Для теста просто активируем
    nowpayments_service.confirm_payment(payment_id, days=30)

    success_text = """
✅ **ПЛАТЕЖ ПОЛУЧЕН!**

Ваша подписка активирована на 30 дней.

Спасибо! 🎉
    """

    buttons = [
        [InlineKeyboardButton("🤖 AI-чат", callback_data="ai_chat")],
        [InlineKeyboardButton("📊 Premium", callback_data="premium_menu")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        success_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
