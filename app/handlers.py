import aiogram
from aiogram import F,Router,Bot
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import CommandStart,Command
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
import requests
from CounterStrikeBot.app.parser_skins import parser
from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup
from CounterStrikeBot.app.keyboard import start_keyboard,payment
from CounterStrikeBot.config import ADMIN_ID,TOKEN
from datetime import datetime
from CounterStrikeBot.database import BroadCast,User,SessionLocal


router = Router()
bot = Bot(token=TOKEN)

headers = {
    "Referer": "https://www.google.com/"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

class BroadcastState(StatesGroup):
    wait_text = State()


def admin_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊‍ Статистика", callback_data='stats')],
        [InlineKeyboardButton(text='✉️ Рассылка', callback_data='broadcast')],
        [InlineKeyboardButton(text='⚙️ Доп настройки', callback_data='settings')]
    ])
    return keyboard


def back_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Back', callback_data='back')],
    ])
    return keyboard


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Добро пожаловать в админ панель бота 🌍❤️!", reply_markup=admin_main_menu())
        return
    else:
        await message.answer('У вас нет доступа к этой команде.')
        return



@router.callback_query(F.data == 'back')
async def back_menu(callback: CallbackQuery):
    await callback.message.answer("", reply_markup=admin_main_menu())
    await callback.answer('')


@router.callback_query(F.data == 'stats')
async def stats_process(callback: CallbackQuery):
    db = SessionLocal()
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.active == True).count()
    db.close()
    text = f'Статистика:\nВсего пользователей 🕵️: {total_users}\nАктивных пользователей 🎮: {active_users}'
    await callback.message.answer(f'{text}')
    await callback.answer('')


@router.callback_query(F.data == 'broadcast')
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст для рассылки ✉️")
    await state.set_state(BroadcastState.wait_text)
    await callback.answer('')


@router.callback_query(F.data == 'settings')
async def settings(callback: CallbackQuery):
    await callback.message.answer("Я рома тик так ")
    await callback.answer('')


@router.message(BroadcastState.wait_text)
async def broadcast_mess(message: Message, state: FSMContext, bot: Bot):
    broadcast_text = message.text
    db = SessionLocal()
    users_list = db.query(User).filter(User.active == True).all()
    count = 0
    for user in users_list:
        try:
            await bot.send_message(user.telegram_id, broadcast_text)
            count += 1
        except Exception as e:
            print(f'Failed to send to {user.telegram_id}:{e}')
    new_broadcast = BroadCast(message=broadcast_text)
    db.add(new_broadcast)
    db.commit()
    db.close()
    await message.answer(f"Рассылка завершена ✉️ ! Сообщение отправлено {count} пользователям 🕵️.",
                         reply_markup=start_keyboard)
    await state.clear()


@router.message(CommandStart())
async def start_message(message:Message):
    db = SessionLocal()
    exiting = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not exiting:
        new_user = User(telegram_id=message.from_user.id, name=message.from_user.full_name,
                        register_at=datetime.now().isoformat())
        db.add(new_user)
        db.commit()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if message.from_user.id == ADMIN_ID:
        user.premium = True
        db.commit()

    register_at = user.register_at
    premium = user.premium
    db.close()
    if premium is True:
        premium = '✅'
    else:
        premium = '❌'

    welcome_text_message = await message.answer_photo(photo="https://ggate.media/wp-content/uploads/2025/02/vosem-tipov-redkosti-skinov-cs2.png",caption="<b>👋 Добро пожаловать!</b>\n\n<b>CS2_skins_Bot</b> - Shop бот для поиска информации о скинах\n\n📋 <b>Используйте меню</b> ниже для навигации  ",parse_mode='HTML')

    await message.reply(
        f'ℹ️ Вся необходимая информация о вашем профиле\n\n🏷️ <b>Имя:</b> <a href="tg://copy?text=ddddd">{message.from_user.full_name}</a>\n🆔 <b>Мой ID:</b> <a href="tg://copy?text=ddddddd">{message.from_user.id}</a>\n\n📆 <b>Регистрация:</b> <a href="tg://copy?text=fdddd">{register_at}</a>\n🔃 <b>TG Премиум:</b> {message.from_user.is_premium}\n\n🔑 <b>Подписка:</b> {premium}\n🗣️ \n💰 Твой баланс: <a href="tg://copy?text=0.00">0.00 RUB</a>\n',
        reply_markup=start_keyboard, parse_mode="HTML")

@router.callback_query(F.data == 'profile')
async def profile_answer(callback:CallbackQuery):
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()

    register_at = user.register_at
    premium = user.premium
    if premium is True:
        premium = '✅'
    else:
        premium = '❌'

    await callback.answer('')

    db.close()
    await callback.message.reply(
        f'ℹ️ Вся необходимая информация о вашем профиле\n\n🏷️ <b>Имя:</b> <a href="tg://copy?text=ddddd">{callback.from_user.full_name}</a>\n🔗<b>Username:</b> @{callback.from_user.username}\n\n🆔 <b>Мой ID:</b> <a href="tg://copy?text=ddddddd">{callback.message.from_user.id}</a>\n📆 <b>Регистрация:</b> <a href="tg://copy?text=fdddd">{register_at}</a>\n🔃 <b>TG Премиум:</b> {callback.message.from_user.is_premium}\n\n🔑 <b>Подписка:</b> {premium}\n🗣️ <b>Язык:</b> <b>{callback.message.from_user.language_code}</b>\n\n💰 Твой баланс: <a href="tg://copy?text=0.00">0.00 RUB</a>\n',
         parse_mode="HTML",reply_markup=start_keyboard)

@router.callback_query(F.data == 'premium')
async def premium_get(callback:CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔑 Подписка ', callback_data='subscribe')],
        [InlineKeyboardButton(text='🤝 Поддержка бота', callback_data='support_bot')]
    ])
    await callback.answer('')
    await callback.message.answer('🔃 Выберите вариант:', reply_markup=keyboard)

@router.callback_query(F.data == 'subscribe')
async def premium_getting(callback: CallbackQuery):
    prices = [LabeledPrice(label="XTR", amount=250)]

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == str(callback.from_user.id)).first()

    if user and user.premium:
        await callback.answer('❌ У вас уже есть подписка!', show_alert=True)
        db.close()
        return

    db.close()
    await callback.answer('')

    await callback.message.answer_invoice(
        title='🔑 Premium подписка',
        description='• 50 запросов в месяц\n• Доступ к расширенному поиску\n• Приоритетная поддержка',
        prices=prices,
        provider_token='',
        payload='premium_subscription',
        currency='XTR',
        reply_markup=payment
    )


@router.callback_query(F.data == 'support_bot')
async def support_to_bot(callback: CallbackQuery):
    prices = [LabeledPrice(label="XTR", amount=20)]
    await callback.answer('')

    await callback.message.answer_invoice(
        title='🤝 Поддержка бота',
        description='Поддержите разработку бота звездами ⭐',
        prices=prices,
        provider_token='',
        payload='bot_support',
        currency='XTR',
        reply_markup=payment,
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


# ✅ ЕДИНСТВЕННЫЙ обработчик successful_payment
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment_system = message.successful_payment
    payload = payment.invoice_payload  # Получаем payload
    user_id = str(message.from_user.id)

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()

    if not user:

        user = User(telegram_id=user_id, name=message.from_user.full_name)
        db.add(user)
        db.commit()

    # Обрабатываем разные типы платежей
    if payload == 'premium_subscription':
        # Покупка подписки
        user.premium = True

        db.commit()

        await message.answer(
            f"✅ **Premium 🔑одписка активирована!**\n\n"
            f"⭐ Получено: {payment.total_amount} звёзд\n"
            f"Спасибо за покупку! 🎉",
             message_effect_id="5104841245755180586"


        )

    elif payload == 'bot_support':
        # Поддержка бота
        # Здесь можно добавить запись в отдельную таблицу донатов
        await message.answer(
            f"🎉 **Спасибо за поддержку!** 🎉\n\n"
            f"⭐ Получено: {payment.total_amount} звёзд\n"
            f"👤 От: {message.from_user.full_name}\n\n"
            f"💝 Ваша поддержка помогает боту развиваться!",
            message_effect_id="5104841245755180586"
        )

    db.close()

@router.callback_query(F.data == 'main_menu')
async def main_menu(callback:CallbackQuery):
    await callback.answer('')
    await callback.message.answer('<b>🏠 Вот главное меню</b>⬇️',parse_mode='HTML',reply_markup=start_keyboard)


@router.callback_query(F.data == 'guns')
async def parse_skins(callback: CallbackQuery):
    """
    Парсер скинов с показом по 10 штук
    """
    await callback.answer()



    # Показываем сообщение о загрузке
    msg = await callback.message.edit_text(
        "⏳ Загружаю скины с CS:GO маркета...\n"
        "Пожалуйста, подождите."
    )

    # Получаем скины если еще не загружены
    if not parser.all_skins:
        await parser.fetch_skins()

    if not parser.all_skins:
        error_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await msg.edit_text("❌ Не удалось загрузить скины", reply_markup=error_keyboard)
        return

    # Начинаем с первой десятки
    current_start = 0
    total_skins = parser.get_total_count()

    # Показываем первые 10 скинов
    await show_skins_batch(callback.message, current_start, total_skins)


async def show_skins_batch(message: Message, start_index: int, total: int):
    """
    Показывает 10 скинов и спрашивает о продолжении
    """


    batch = parser.get_batch(start_index, 10)
    end_index = min(start_index + 10, total)

    if not batch:
        stop_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="skin_restart")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await message.answer("✅ Все скины показаны!", reply_markup=stop_keyboard)
        return

    # Формируем сообщение с 10 скинами
    text = (
        f"<b>🎮 Скины {start_index + 1}-{end_index} из {total}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for i, skin in enumerate(batch, start=start_index):
        name = skin['market_hash_name']
        price = skin['min_price'] or skin['suggested_price'] or 0
        currency = skin['currency']
        quantity = skin['quantity'] or 0

        # Добавляем эмодзи в зависимости от типа
        if any(x in name.lower() for x in ['knife', 'нож', 'bayonet', 'karambit']):
            emoji = "🔪"
        elif any(x in name.lower() for x in ['ak-47', 'm4', 'awp']):
            emoji = "🔫"
        elif any(x in name.lower() for x in ['glock', 'usp', 'deagle']):
            emoji = "🔰"
        elif any(x in name.lower() for x in ['glove', 'перчатки']):
            emoji = "🧤"
        elif any(x in name.lower() for x in ['sticker', 'наклейка']):
            emoji = "🏷️"
        elif any(x in name.lower() for x in ['case', 'кейс', 'capsule']):
            emoji = "📦"
        else:
            emoji = "🎯"

        # Определяем износ
        wear_emoji = ""
        if "(Factory New)" in name:
            wear_emoji = "🌟"
        elif "(Minimal Wear)" in name:
            wear_emoji = "✨"
        elif "(Field-Tested)" in name:
            wear_emoji = "⚔️"
        elif "(Well-Worn)" in name:
            wear_emoji = "📦"
        elif "(Battle-Scarred)" in name:
            wear_emoji = "💥"

        text += f"{emoji}{wear_emoji} <b>{i + 1}.</b> <code>{name[:45]}</code>\n"
        text += f"   💰 {price} {currency} | 📦 {quantity} шт.\n\n"


    # Создаем клавиатуру для продолжения
    if end_index < total:
        continue_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Показать следующие 10", callback_data=f"skin_batch:{end_index}")],
            [InlineKeyboardButton(text="⏹️ Завершить", callback_data="skin_stop")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await message.edit_text(f'{text}\n📎 <b>Ссылка на сайт :</b> <a href="https://skinport.com/market/">Вот ссылка</a>', reply_markup=continue_keyboard, parse_mode="HTML")
    else:
        final_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="skin_restart")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await message.edit_text(text + "\n✅ Это были все скины!", reply_markup=final_keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith('skin_batch:'))
async def skin_next_batch(callback: CallbackQuery):
    """
    Показывает следующую партию из 10 скинов
    """
    await callback.answer()

    next_start = int(callback.data.split(':')[1])


    await show_skins_batch(callback.message, next_start, parser.get_total_count())


@router.callback_query(F.data == 'skin_stop')
async def skin_stop(callback: CallbackQuery):
    """
    Останавливает показ скинов
    """
    await callback.answer()

    stop_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="skin_restart")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        "⏹️ Показ скинов остановлен.\n"
        "Что делаем дальше?",
        reply_markup=stop_keyboard
    )


@router.callback_query(F.data == 'skin_restart')
async def skin_restart(callback: CallbackQuery):
    """
    Перезапускает показ скинов с начала
    """
    await callback.answer()



    if parser.all_skins:
        await show_skins_batch(callback.message, 0, parser.get_total_count())
    else:
        error_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ])
        await callback.message.edit_text("❌ Скины не найдены", reply_markup=error_keyboard)
