async def handle_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    signals_text = """
    🚀 **ПОСЛЕДНИЕ 5 СИГНАЛОВ:**

    [Здесь будут последние 5 сигналов из БД]

    Или подпишитесь на закрытый канал для более полной информации.
    """

    await query.edit_message_text(signals_text, parse_mode='Markdown')


async def handle_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Получение последних аналитических постов
    analytics_text = """
    📊 **ПОСЛЕДНИЕ ОБЗОРЫ:**

    [Последние аналитические посты из канала]
    """

    await query.edit_message_text(analytics_text, parse_mode='Markdown')