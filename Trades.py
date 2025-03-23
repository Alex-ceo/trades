import logging
import os
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.ext import CallbackContext

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger("game_shop_bot")

# Состояния для обработчика диалогов
ВЫБОРКОЛИЧЕСТВА, ВЫБОРДЕЙСТВИЯ, ВЫБОРБУСТА, ВЫБОРАКЦИИ, ВЫБОРГОЛДЫ, ВЫБОРСКИНА, ВЫБОРСКРИПТА = range(7)

# ID чата владельца бота - замените на ваш ID
IDВЛАДЕЛЬЦА = "790387076"

# Цены на товары (добавлено по запросу)
ЦЕНЫ = {
    'gems': {
        '100': 100,
        '500': 450,
        '1000': 800
    },
    'boost_bs': 300,
    'boost_cs': 350,
    'gold': {
        '1000': 150,
        '5000': 600,
        '10000': 1000
    },
    'skins': {
        'default': 300  # Стандартная цена, можно изменить для каждого скина
    },
    'scripts': {
        'semi_api': 500,
        'script003': 400,
        'opr_custom': 600,
        'nakly': 200,
        'background': 150
    },
    'promo': {
        'default': 250  # Стандартная цена для акций
    }
}

async def старт(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляем сообщение при команде /start."""
    пользователь = update.effective_user
    клавиатура_главного_меню = [
        [InlineKeyboardButton("Brawl Stars", callback_data='brawl_stars')],
        [InlineKeyboardButton("CS2", callback_data='cs2')],
        [InlineKeyboardButton("Корзина", callback_data='cart')],
        [InlineKeyboardButton("Отзывы", callback_data='reviews')]
    ]
    разметка_ответа = InlineKeyboardMarkup(клавиатура_главного_меню)
    await update.message.reply_text(
        f"Привет, {пользователь.first_name}! Выберите игру:",
        reply_markup=разметка_ответа
    )

async def обработка_кнопок(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем нажатия кнопок."""
    запрос = update.callback_query
    await запрос.answer()

    if запрос.data == 'brawl_stars':
        # Меню Brawl Stars
        клавиатура = [
            [InlineKeyboardButton("Купить гемы", callback_data='buy_gems')],
            [InlineKeyboardButton("Купить буст", callback_data='buy_boost_bs')],
            [InlineKeyboardButton("Купить акцию", callback_data='buy_promo_bs')]
        ]
        # Кнопка назад в главное меню внизу
        клавиатура.append([InlineKeyboardButton("Назад", callback_data='back_main')])
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите опцию Brawl Stars:", reply_markup=разметка_ответа)
        return ConversationHandler.END

    elif запрос.data == 'cs2':
        # Меню CS2
        клавиатура = [
            [InlineKeyboardButton("Купить голду", callback_data='buy_gold')],
            [InlineKeyboardButton("Купить скрипт", callback_data='buy_script')],
            [InlineKeyboardButton("Купить скин", callback_data='buy_skin')],
            [InlineKeyboardButton("Купить акцию", callback_data='buy_promo_cs')],
            [InlineKeyboardButton("Купить буст", callback_data='buy_boost_cs')]
        ]
        # Кнопка назад в главное меню внизу
        клавиатура.append([InlineKeyboardButton("Назад", callback_data='back_main')])
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите опцию CS2:", reply_markup=разметка_ответа)
        return ConversationHandler.END


    elif запрос.data == 'back_main':
        # Возврат в главное меню
        клавиатура_главного_меню = [
            [InlineKeyboardButton("Brawl Stars", callback_data='brawl_stars')],
            [InlineKeyboardButton("CS2", callback_data='cs2')],
            [InlineKeyboardButton("Корзина", callback_data='cart')],
            [InlineKeyboardButton("Отзывы", callback_data='reviews')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура_главного_меню)
        await запрос.edit_message_text(text="Главное меню:", reply_markup=разметка_ответа)
        return ConversationHandler.END

    elif запрос.data == 'buy_gems':
        # Показываем варианты покупки гемов с ценами
        клавиатура = [
            [InlineKeyboardButton(f"100 гемов - {ЦЕНЫ['gems']['100']} руб.", callback_data='gems_100')],
            [InlineKeyboardButton(f"500 гемов - {ЦЕНЫ['gems']['500']} руб.", callback_data='gems_500')],
            [InlineKeyboardButton(f"1000 гемов - {ЦЕНЫ['gems']['1000']} руб.", callback_data='gems_1000')],
            [InlineKeyboardButton("Назад", callback_data='brawl_stars')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите количество гемов:", reply_markup=разметка_ответа)
        return ВЫБОРКОЛИЧЕСТВА

    elif запрос.data.startswith('gems_'):
        количество = запрос.data.split('_')[1]
        цена = ЦЕНЫ['gems'][количество]
        
        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []
            
        context.user_data['корзина'].append(f"Гемы: {количество} - {цена} руб.")
        
        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='brawl_stars')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(
            text=f"{количество} гемов добавлено в корзину!",
            reply_markup=разметка_ответа
        )
        
        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: {количество} гемов")
        return ConversationHandler.END

    elif запрос.data == 'buy_boost_bs' or запрос.data == 'buy_boost_cs':
        игра = "Brawl Stars" if запрос.data == 'buy_boost_bs' else "CS2"
        цена = ЦЕНЫ['boost_bs'] if запрос.data == 'buy_boost_bs' else ЦЕНЫ['boost_cs']
        
        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []
            
        context.user_data['корзина'].append(f"Буст для {игра} - {цена} руб.")
        
        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='back_main')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(
            text=f"Буст для {игра} добавлен в корзину!",
            reply_markup=разметка_ответа
        )
        
        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: Буст для {игра}")
        return ConversationHandler.END

    elif запрос.data == 'buy_promo_bs' or запрос.data == 'buy_promo_cs':
        игра = "Brawl Stars" if запрос.data == 'buy_promo_bs' else "CS2"
        context.user_data['текущая_игра'] = игра
        context.user_data['ожидание_ввода'] = 'описание_акции'
        await запрос.edit_message_text(text=f"Какую акцию для {игра} вы хотите приобрести? Опишите:")
        return ВЫБОРАКЦИИ


    elif запрос.data == 'buy_gold':
        # Показываем варианты покупки голды с ценами
        клавиатура = [
            [InlineKeyboardButton(f"1000 голды - {ЦЕНЫ['gold']['1000']} руб.", callback_data='gold_1000')],
            [InlineKeyboardButton(f"5000 голды - {ЦЕНЫ['gold']['5000']} руб.", callback_data='gold_5000')],
            [InlineKeyboardButton(f"10000 голды - {ЦЕНЫ['gold']['10000']} руб.", callback_data='gold_10000')],
            [InlineKeyboardButton("Назад", callback_data='cs2')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите количество голды:", reply_markup=разметка_ответа)
        return ВЫБОРГОЛДЫ

    elif запрос.data.startswith('gold_'):
        количество = запрос.data.split('_')[1]
        цена = ЦЕНЫ['gold'][количество]
        
        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []
            
        context.user_data['корзина'].append(f"Голда: {количество} - {цена} руб.")
        
        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='cs2')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(
            text=f"{количество} голды добавлено в корзину!",
            reply_markup=разметка_ответа
        )
        
        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: {количество} голды")
        return ConversationHandler.END

    elif запрос.data == 'buy_skin':
        context.user_data['ожидание_ввода'] = 'тип_скина'
        await запрос.edit_message_text(text="Какой скин вы хотите приобрести?")
        return ВЫБОРСКИНА

    elif запрос.data == 'buy_script':
        клавиатура = [
            [InlineKeyboardButton(f"Полу апи - {ЦЕНЫ['scripts']['semi_api']} руб.", callback_data='semi_api')],
            [InlineKeyboardButton(f"Скрипт003 - {ЦЕНЫ['scripts']['script003']} руб.", callback_data='script003')],
            [InlineKeyboardButton(f"ОПР (кастом) - {ЦЕНЫ['scripts']['opr_custom']} руб.", callback_data='opr_custom')],
            [InlineKeyboardButton(f"Наклы - {ЦЕНЫ['scripts']['nakly']} руб.", callback_data='nakly')],
            [InlineKeyboardButton(f"Фон - {ЦЕНЫ['scripts']['background']} руб.", callback_data='background')],
            [InlineKeyboardButton("Назад", callback_data='cs2')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите скрипт:", reply_markup=разметка_ответа)
        return ВЫБОРСКРИПТА

    elif запрос.data in ['semi_api', 'script003', 'opr_custom', 'nakly', 'background']:
        типы_скриптов = {
            'semi_api': 'Полу апи',
            'script003': 'Скрипт003',
            'opr_custom': 'ОПР (кастом)',
            'nakly': 'Наклы',
            'background': 'Фон'
        }
        
        цена = ЦЕНЫ['scripts'][запрос.data]

        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []

        context.user_data['корзина'].append(f"Скрипт: {типы_скриптов[запрос.data]} - {цена} руб.")

        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='cs2')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(
            text=f"Скрипт '{типы_скриптов[запрос.data]}' добавлен в корзину!",
            reply_markup=разметка_ответа
        )

        # Уведомляем владельца
        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: Скрипт {типы_скриптов[запрос.data]}")
        return ConversationHandler.END


    elif запрос.data == 'cart':
        if 'корзина' not in context.user_data or not context.user_data['корзина']:
            await запрос.edit_message_text(
                text="Ваша корзина пуста.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data='back_main')]])
            )
        else:
            текст_корзины = "Ваша корзина:\n" + "\n".join(context.user_data['корзина'])
            
            # Подсчет общей суммы (для демонстрации)
            общая_сумма = 0
            for item in context.user_data['корзина']:
                # Извлечение цены из строки товара
                if " - " in item and " руб." in item:
                    цена_текст = item.split(" - ")[1].replace(" руб.", "")
                    try:
                        общая_сумма += float(цена_текст)
                    except:
                        pass
            
            текст_корзины += f"\n\nОбщая сумма: {общая_сумма} руб."
            
            клавиатура = [
                [InlineKeyboardButton("Оформить заказ", callback_data='checkout')],
                [InlineKeyboardButton("Очистить корзину", callback_data='clear_cart')],
                [InlineKeyboardButton("Назад в меню", callback_data='back_main')]
            ]
            разметка_ответа = InlineKeyboardMarkup(клавиатура)
            await запрос.edit_message_text(text=текст_корзины, reply_markup=разметка_ответа)
        return ConversationHandler.END

    elif запрос.data == 'clear_cart':
        context.user_data['корзина'] = []
        await запрос.edit_message_text(
            text="Корзина очищена.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data='back_main')]])
        )
        return ConversationHandler.END

    elif запрос.data == 'checkout':
        # Здесь должна быть интеграция со Stripe, PayPal или Crypto Bot
        клавиатура = [
            [InlineKeyboardButton("Оплатить через Stripe", callback_data='pay_stripe')],
            [InlineKeyboardButton("Оплатить через PayPal", callback_data='pay_paypal')],
            [InlineKeyboardButton("Оплатить через Crypto Bot", callback_data='pay_crypto')],
            [InlineKeyboardButton("Отмена", callback_data='cancel')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Выберите способ оплаты:", reply_markup=разметка_ответа)
        return ConversationHandler.END

    elif запрос.data in ['pay_stripe', 'pay_paypal', 'pay_crypto']:
        # Имитация обработки платежа
        способ_оплаты = {
            'pay_stripe': "Stripe",
            'pay_paypal': "PayPal",
            'pay_crypto': "Crypto Bot"
        }[запрос.data]
        
        await запрос.edit_message_text(text=f"Перенаправление на {способ_оплаты} для оплаты...")

        # В реальной реализации здесь должна быть генерация ссылки на оплату
        # Инструкции по настройке платежных систем:
        # 1. Stripe: Создайте аккаунт на stripe.com, получите API ключи и используйте stripe-python библиотеку
        # 2. PayPal: Зарегистрируйтесь в PayPal Developer, создайте приложение и используйте paypalrestsdk
        # 3. Crypto Bot: Обратитесь к документации @CryptoBot и настройте оплату через их API

        товары_корзины = "\n".join(context.user_data.get('корзина', ['Корзина пуста']))
        общая_сумма = 0
        for item in context.user_data['корзина']:
            if " - " in item and " руб." in item:
                цена_текст = item.split(" - ")[1].replace(" руб.", "")
                try:
                    общая_сумма += float(цена_текст)
                except:
                    pass
                    
        await уведомить_владельца(context, f"Новый заказ от пользователя {update.effective_user.id}:\n{товары_корзины}\nОбщая сумма: {общая_сумма} руб.\nМетод оплаты: {способ_оплаты}")

        # Очищаем корзину после оформления заказа
        context.user_data['корзина'] = []


        # После задержки отправляем подтверждение
        await запрос.message.reply_text("Оплата обрабатывается. Спасибо за заказ!")
        return ConversationHandler.END

    elif запрос.data == 'reviews':
        клавиатура = [
            [InlineKeyboardButton("Оставить отзыв", callback_data='leave_review')],
            [InlineKeyboardButton("Назад", callback_data='back_main')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        await запрос.edit_message_text(text="Отзывы о нашем сервисе:", reply_markup=разметка_ответа)
        return ConversationHandler.END

    elif запрос.data == 'leave_review':
        await запрос.edit_message_text(text="Пожалуйста, напишите ваш отзыв в следующем сообщении:")
        context.user_data['ожидание_отзыва'] = True
        return ConversationHandler.END

    elif запрос.data == 'cancel':
        await запрос.edit_message_text(
            text="Операция отменена.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад в меню", callback_data='back_main')]])
        )
        return ConversationHandler.END

    return ConversationHandler.END

async def обработка_сообщений(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатываем сообщения пользователя."""
    if 'ожидание_отзыва' in context.user_data and context.user_data['ожидание_отзыва']:
        текст_отзыва = update.message.text
        
        клавиатура = [[InlineKeyboardButton("Назад в меню", callback_data='back_main')]]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        
        await update.message.reply_text("Спасибо за отзыв!", reply_markup=разметка_ответа)
        context.user_data['ожидание_отзыва'] = False

        # Уведомляем владельца о новом отзыве
        await уведомить_владельца(context, f"Новый отзыв от пользователя {update.effective_user.id}:\n{текст_отзыва}")
        return ConversationHandler.END

    # Обработка ввода скина
    if context.user_data.get('ожидание_ввода') == 'тип_скина':
        тип_скина = update.message.text
        цена = ЦЕНЫ['skins']['default']  # Стандартная цена для скина
        
        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []
            
        context.user_data['корзина'].append(f"Скин: {тип_скина} - {цена} руб.")
        
        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='cs2')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        
        await update.message.reply_text(
            f"Скин '{тип_скина}' добавлен в корзину!",
            reply_markup=разметка_ответа
        )
        
        # Уведомляем владельца
        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: Скин {тип_скина}")
        
        context.user_data['ожидание_ввода'] = None
        return ВЫБОРДЕЙСТВИЯ
        
    # Обработка ввода описания акции
    if context.user_data.get('ожидание_ввода') == 'описание_акции':
        описание_акции = update.message.text
        игра = context.user_data.get('текущая_игра', 'неизвестная игра')
        цена = ЦЕНЫ['promo']['default']  # Стандартная цена для акции
        
        if 'корзина' not in context.user_data:
            context.user_data['корзина'] = []
            
        context.user_data['корзина'].append(f"Акция для {игра}: {описание_акции} - {цена} руб.")
        
        клавиатура = [
            [InlineKeyboardButton("Перейти в корзину", callback_data='cart')],
            [InlineKeyboardButton("Продолжить покупки", callback_data='back_main')]
        ]
        разметка_ответа = InlineKeyboardMarkup(клавиатура)
        
        await update.message.reply_text(
            f"Акция для {игра} добавлена в корзину!",
            reply_markup=разметка_ответа
        )
        
        # Уведомляем владельца

        await уведомить_владельца(context, f"Новый товар в корзине пользователя {update.effective_user.id}: Акция для {игра}: {описание_акции}")
        
        context.user_data['ожидание_ввода'] = None
        return ВЫБОРДЕЙСТВИЯ
        
    return ConversationHandler.END

async def уведомить_владельца(context, сообщение):
    """Отправляем уведомление владельцу бота."""
    try:
        await context.bot.send_message(chat_id=IDВЛАДЕЛЬЦА, text=сообщение)
    except Exception as e:
        logger.error(f"Не удалось уведомить владельца: {e}")

def главная() -> None:
    """Запускаем бота."""
    # Создаем приложение и передаем токен бота
    # ВНИМАНИЕ: Используйте свой токен, а не этот пример!
    # Этот токен был указан в коде и возможно недействительный
    # Для получения токена создайте бота через @BotFather в Telegram

    приложение = Application.builder().token("7665784307:AAE8keh9JNbWNSEDw7hYbR0Q1nUX6QDeofU").build()
    # Добавляем обработчики команд
    приложение.add_handler(CommandHandler("start", старт))
    
    # Добавляем обработчик для кнопок
    приложение.add_handler(CallbackQueryHandler(обработка_кнопок))
    
    # Добавляем обработчик для обычных сообщений
    приложение.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, обработка_сообщений))
    
    # Запускаем бота
    приложение.run_polling()

if __name__ == "__main__":
    главная()
