from services.subscription_service import SubscriptionService


async def handle_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    sub_info = SubscriptionService.get_subscription_info(user_id)

    if sub_info['active']:
        account_text = f"""
        📅 **ВАШ АККАУНТ:**

        Подписка активна до: {sub_info['until']}

        Выберите действие:
        """
    else:
        account_text = "У вас нет активной подписки. Пожалуйста, приобретите доступ."

    await query.edit_message_text(account_text, parse_mode='Markdown')