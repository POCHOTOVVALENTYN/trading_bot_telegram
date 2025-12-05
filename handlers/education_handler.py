async def handle_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lessons = {
        'intro': '📚 Введение: Основы рынка и терминология',
        'lesson1': '📈 Урок 1: Технический Анализ (База)',
        'lesson2': '📉 Урок 2: Риск-менеджмент',
        'lesson3': '🧠 Урок 3: Психология Трейдинга',
        'lesson4': '⛓️ Урок 4: Анализ On-chain',
        'test': '📝 Финальный Тест'
    }

    buttons = [[InlineKeyboardButton(text, callback_data=key)] for key, text in lessons.items()]
    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        "🎓 **ОБУЧАЮЩИЙ КУРС:**",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )