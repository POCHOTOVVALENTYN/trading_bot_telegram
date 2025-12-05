from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_free_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("🌟 Получить Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("🎁 Что внутри Premium?", callback_data="show_premium_features")],
        [InlineKeyboardButton("📚 Бесплатные ресурсы", callback_data="free_resources")],
        [InlineKeyboardButton("👨‍💻 Об авторе", callback_data="about_author")],
        [InlineKeyboardButton("📞 Поддержка / FAQ", callback_data="support")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_premium_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("🤖 AI-клон-Аналитик", callback_data="ai_chat")],
        [InlineKeyboardButton("🚀 Сигналы (Futures)", callback_data="signals")],
        [InlineKeyboardButton("📊 Premium-Аналитика", callback_data="analytics")],
        [InlineKeyboardButton("💡 Авторские рекомендации", callback_data="recommendations")],
        [InlineKeyboardButton("🎓 Обучающий курс", callback_data="education")],
        [InlineKeyboardButton("⚙️ Мой аккаунт", callback_data="account")],
        [InlineKeyboardButton("👑 Поддержка", callback_data="support_premium")]
    ]
    return InlineKeyboardMarkup(buttons)