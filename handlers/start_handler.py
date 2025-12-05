from telegram import Update
from telegram.ext import ContextTypes
from services.auth_service import AuthService
from keyboards.main_keyboards import get_free_menu_keyboard, get_premium_menu_keyboard
from services.subscription_service import SubscriptionService


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Создаем пользователя в БД
    AuthService.get_or_create_user(
        user.id,
        user.username,
        user.first_name
    )

    # Проверяем статус подписки
    has_premium = SubscriptionService.check_premium_status(user.id)

    if has_premium:
        # Premium меню
        welcome_text = f"Здравствуйте, {user.first_name}! Рад вас видеть. Выберите, с чего начнем:"
        keyboard = get_premium_menu_keyboard()
        context.user_data['menu'] = 'premium'
    else:
        # Free меню
        welcome_text = """Здравствуйте! Я — бот Евгения, профессионального трейдера. Здесь вы можете получить доступ к его эксклюзивной аналитике, торговым сигналам и уникальному AI-клону-ассистенту. Выберите опцию:"""
        keyboard = get_free_menu_keyboard()
        context.user_data['menu'] = 'free'

    await update.message.reply_text(welcome_text, reply_markup=keyboard)