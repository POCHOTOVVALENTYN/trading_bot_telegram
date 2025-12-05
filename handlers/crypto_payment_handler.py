async def handle_buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать доступные способы оплаты"""
    query = update.callback_query
    await query.answer()

    payment_text = """
💰 **ВЫБЕРИТЕ СПОСОБ ОПЛАТЫ И ТАРИФ:**

🌐 **TON Wallet** (Встроена в Telegram)
   • Комиссия: 0.1-0.5%
   • Скорость: 1-3 сек
   • Самая удобная

🔗 **USDT TRC20** (Tron)
   • Комиссия: $0.1-1
   • Скорость: 1-2 мин
   • Популярна в СНГ

🌍 **NOWPayments** (100+ криптовалют)
   • Комиссия: 0.5-1%
   • Скорость: 5-30 мин
   • Самая гибкая

_Выберите способ оплаты:_
    """

    # Создаем кнопки для каждого метода и тарифа
    buttons = [
        [InlineKeyboardButton("🌐 TON Wallet", callback_data="payment_method_ton")],
        [InlineKeyboardButton("🔗 USDT TRC20", callback_data="payment_method_tron")],
        [InlineKeyboardButton("🌍 NOWPayments", callback_data="payment_method_now")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        payment_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_choose_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор тарифа после выбора метода оплаты"""
    query = update.callback_query
    await query.answer()

    method = query.data.split('_')[-1]  # payment_method_ton -> ton
    context.user_data['payment_method'] = method

    from config import TARIFFS

    tariff_text = "💎 **ВЫБЕРИТЕ ТАРИФ:**\n\n"

    buttons = []
    for code, info in TARIFFS.items():
        button_text = f"{info['name']} (${info['price_usdt']}/мес)"
        callback = f"pay_{method}_{code}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=callback)])

    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="buy_premium")])

    keyboard = InlineKeyboardMarkup(buttons)

    for code, info in TARIFFS.items():
        tariff_text += f"\n**{info['name']}** - ${info['price_usdt']}/мес\n"
        for feature in info['features']:
            tariff_text += f"  • {feature}\n"

    await query.edit_message_text(
        tariff_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

