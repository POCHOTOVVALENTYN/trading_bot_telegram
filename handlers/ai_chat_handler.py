from services.ai_service import AIService


async def handle_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['mode'] = 'ai_chat'

    await query.edit_message_text(
        "🤖 Вы вошли в режим AI-Аналитика. Задавайте вопросы о рынке, проектах, стратегиях.",
        reply_markup=get_exit_button()
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('mode') != 'ai_chat':
        return

    user_message = update.message.text

    # Запрос к AI сервису
    ai_response = AIService.get_ai_response(user_message)

    disclaimer = "\n\n⚠️ *Это аналитика в образовательных целях, не инвестиционный совет.*"

    await update.message.reply_text(
        ai_response + disclaimer,
        parse_mode='Markdown'
    )