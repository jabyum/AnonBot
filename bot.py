import re
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.utils.deep_linking import create_start_link
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, CallbackQuery, LabeledPrice
from buttons import *
from states import Links
from database.userservice import *
bot_router = Router()
async def check_channels(message):
    all_channels = get_channels_for_check()
    if all_channels != []:
        for i in all_channels:
            try:
                check = await message.bot.get_chat_member(i[0], user_id=message.from_user.id)
                if check.status in ["left"]:
                    await message.bot.send_message(chat_id=message.from_user.id,
                                                   text="Для использования бота подпишитесь на наших спонсоров",
                                                   reply_markup=await channels_in(all_channels))
                    return False

            except:
                pass
    return True
async def payment(message, amount):
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title="Поддержка бота",
        description=f"Поддержать бота на {amount} звёзд!",
        prices=prices,
        provider_token="",
        payload="bot_support",
        currency="XTR",
        reply_markup=await payment_keyboard(amount),
    )
@bot_router.message(CommandStart())
async def start(message: Message, state: FSMContext, command: BotCommand = None):
    channels_checker = await check_channels(message)
    checker = check_user(message.from_user.id)
    if not channels_checker:
        if not checker:
            new_link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
            link_for_db = new_link[new_link.index("=")+1:]
            add_user(message.from_user.id, link_for_db)
    else:
        if not checker:
            new_link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
            link_for_db = new_link[new_link.index("=") + 1:]
            add_user(message.from_user.id, link_for_db)

        if command.args:
            if not checker:
                new_link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
                link_for_db = new_link[new_link.index("=") + 1:]
                add_user(message.from_user.id, link_for_db)
                await message.bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать в анонимный чат!",
                                               reply_markup= await main_menu_bt())
            link_user = get_user_by_link(command.args)
            if link_user:
                add_link_statistic(link_user)
                greeting = get_greeting(link_user)
                await message.bot.send_message(chat_id=message.from_user.id,
                                               text="🚀 Здесь можно <b>отправить анонимное сообщение человеку</b>, который опубликовал "
                                                    "эту ссылку.\n\n"
                                                    "Напишите сюда всё, что хотите ему передать, и через несколько секунд он "
                                                    "получит ваше сообщение, но не будет знать от кого.\n\n"
                                                    "Отправить можно фото, видео, 💬 текст, 🔊 голосовые, 📷видеосообщения "
                                                    "(кружки), а также стикеры.\n\n"
                                                    "⚠️<b> Это полностью анонимно!</b>", reply_markup=await cancel_in(),
                                               parse_mode="html")
                if greeting:
                    await message.bot.send_message(chat_id=message.from_user.id, text=greeting)
                await state.set_state(Links.send_st)
                await state.set_data({"link_user": link_user})
        if not command.args:
            link = await create_start_link(message.bot, get_user_link(message.from_user.id))
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text=f"🚀 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n"
                                                f"Твоя личная ссылка:\n👉{link}\n\n"
                                                f"Размести эту ссылку ☝️ в своём профиле Telegram/Instagram/TikTok или "
                                                f"других соц сетях, чтобы начать получать сообщения 💬", parse_mode="html",
                                           reply_markup=await main_menu_bt())
@bot_router.callback_query(F.data.in_(["check_chan", "cancel", "pay10", "pay20", "pay50", "pay100", "pay500",
                                       "greeting_rem"]))
async def call_backs(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "check_chan":
        checking = await check_channels(query)
        await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        if checking:
            await query.bot.send_message(chat_id=query.from_user.id, text="<b>Готово!\n\n"
                                                                          "Чтобы задать вопрос вашему другу, перейдите по"
                                                                          " его ссылке ещё раз 🔗</b>",
                                         parse_mode="html", reply_markup=await main_menu_bt())
    if query.data == "cancel":
        await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        link = await create_start_link(query.bot, get_user_link(query.from_user.id))
        await query.bot.send_message(chat_id=query.from_user.id,
                                     text=f"🚀 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n"
                                          f"Твоя личная ссылка:\n👉{link}\n\n"
                                          f"Размести эту ссылку ☝️ в своём профиле Telegram/Instagram/TikTok или "
                                          f"других соц сетях, чтобы начать получать сообщения 💬",
                                     parse_mode="html",
                                     reply_markup=await main_menu_bt())
    elif query.data == "pay10":
        await payment(query.message, 10)
    elif query.data == "pay20":
        await payment(query.message, 20)
    elif query.data == "pay50":
        await payment(query.message, 50)
    elif query.data == "pay100":
        await payment(query.message, 100)
    elif query.data == "pay500":
        await payment(query.message, 500)
    elif query.data == "greeting_rem":
        await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        change_greeting_user(tg_id=query.from_user.id)
        await query.bot.send_message(chat_id=query.from_user.id, text="Отлично!\n\n"
                                                                      "👋 Приветствие очищено!",
                                     reply_markup= await main_menu_bt())



@bot_router.callback_query(lambda call: "again_" in call.data)
async def again(query: CallbackQuery, state: FSMContext):
    link_user = int(query.data.replace("again_", ""))
    await query.bot.send_message(chat_id=query.from_user.id,
                                 text="🚀 Здесь можно <b>отправить анонимное сообщение человеку</b>, который опубликовал "
                                        "эту ссылку.\n\n"
                                        "Напишите сюда всё, что хотите ему передать, и через несколько секунд он "
                                        "получит ваше сообщение, но не будет знать от кого.\n\n"
                                        "Отправить можно фото, видео, 💬 текст, 🔊 голосовые, 📷видеосообщения "
                                        "(кружки), а также стикеры.\n\n"
                                        "⚠️<b> Это полностью анонимно!</b>", reply_markup=await cancel_in(),
                                 parse_mode="html")
    await state.set_state(Links.send_st)
    await state.set_data({"link_user": link_user})


@bot_router.message(Links.send_st)
async def anon_mes(message: Message, state: FSMContext):
    get_link = await state.get_data()
    receiver = get_link.get("link_user")
    sender_message_id = message.message_id
    text1 = "<b>У тебя новое анонимное сообщение!</b>\n\n"
    text2 = "↩️<i> Свайпни для ответа.</i>"
    caption = ""
    if message.caption:
        caption = message.caption + "\n\n"
    try:
        if message.voice:
            receiver_message = await message.bot.copy_message(chat_id=receiver, from_chat_id=message.from_user.id,
                                                              message_id=message.message_id, caption="<b>У тебя новое анонимное сообщение!</b>\n\n"
                                                                                                     "↩️<i>Свайпни для ответа.</i>",
                                                              parse_mode="html")
            await message.bot.send_message(chat_id=message.from_user.id, text="Сообщение отправлено, ожидайте ответ!",
                                           reply_markup=await again_in(receiver))
            add_messages_info(sender_id=message.from_user.id, receiver_id=receiver, sender_message_id=sender_message_id,
                              receiver_message_id=receiver_message.message_id)
            await state.clear()
        elif message.video_note or message.sticker:
            await message.bot.copy_message(chat_id=receiver, from_chat_id=message.from_user.id,
                                           message_id=message.message_id)
            receiver_message = await message.bot.send_message(chat_id=receiver, text="<b>У тебя новое анонимное сообщение!</b>\n\n"
                                                                                     "↩️<i>Свайпни для ответа.</i>", parse_mode="html")
            await message.bot.send_message(chat_id=message.from_user.id, text="Сообщение отправлено, ожидайте ответ!",
                                           reply_markup=await again_in(receiver))
            add_messages_info(sender_id=message.from_user.id, receiver_id=receiver, sender_message_id=sender_message_id,
                              receiver_message_id=receiver_message.message_id)
            await state.clear()
        elif message.video or message.photo or message.document:
            receiver_message = await message.bot.copy_message(chat_id=receiver, from_chat_id=message.from_user.id,
                                                              message_id=message.message_id, caption=text1+caption+text2,
                                                              parse_mode="html")
            await message.bot.send_message(chat_id=message.from_user.id, text="Сообщение отправлено, ожидайте ответ!",
                                           reply_markup=await again_in(receiver))
            add_messages_info(sender_id=message.from_user.id, receiver_id=receiver, sender_message_id=sender_message_id,
                              receiver_message_id=receiver_message.message_id)
            await state.clear()
        elif message.text:
            receiver_message = await message.bot.send_message(chat_id=receiver, text=text1+message.text+"\n\n"+text2, parse_mode="html")
            await message.bot.send_message(chat_id=message.from_user.id, text="Сообщение отправлено, ожидайте ответ!",
                                           reply_markup=await again_in(receiver))
            add_messages_info(sender_id=message.from_user.id, receiver_id=receiver, sender_message_id=sender_message_id,
                              receiver_message_id=receiver_message.message_id)
            await state.clear()
        else:
            await message.bot.send_message(message.from_user.id, "️️❗Ошибка. Неподдерживаемый формат", reply_markup= await main_menu_bt())
            await state.clear()
    except:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка. Не удалось отправить сообщение",
                                       reply_markup=await main_menu_bt())
        await state.clear()
@bot_router.message(Links.change_greeting)
async def change_greeting(message: Message, state: FSMContext):
    if message.text:
        new_greeting = "👋" + message.text
        if 4 < len(new_greeting) < 301:
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text="👋 Приветствие не может быть короче 5 и длиннее 300 символов.\n"
                                                "Пожалуйста, попробуйте заново.", reply_markup=await main_menu_bt())
            await state.clear()
        else:
            await message.bot.send_message(chat_id=message.from_user.id, text=f"Отлично!\n\n"
                                                                              f"Ваше новое приветсвие: {new_greeting}",
                                           reply_markup=await main_menu_bt())
            change_greeting_user(message.from_user.id, new_greeting)
            await state.clear()
    else:
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text="Ошибка! 👋Приветствие может состоять только из символов и эмодзи",
                                       reply_markup=await main_menu_bt())
        await state.clear()
@bot_router.message(Links.change_link)
async def change_link(message: Message, state: FSMContext):
    if message.text:
        check = check_link(message.text)
        pattern = r'^[a-zA-Z0-9_]+$'
        check_pattern = re.search(pattern, message.text)
        if not check:
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text="📛 Такая ссылка уже кем-то используется ;(\n"
                                                "Попробуйте заново",
                                           reply_markup= await main_menu_bt())
            await state.clear()
        elif check_pattern and 6 < len(message.text) < 31:
            change_link_db(message.from_user.id, message.text)
            new_link = await create_start_link(message.bot, message.text)
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text=f"Готово! ✅\n\n"
                                                f"Твоя новая ссылка:\n"
                                                f"🔗<code>{new_link}</code>\n\n"
                                                f"Чтобы скопировать ссылку, просто кликни на неё. "
                                                f"Затем размести в Instagram или других соц. сетях",
                                           parse_mode="html", reply_markup=await main_menu_bt())
            await state.clear()
        else:
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text="Ошибка! 📛 Новая ссылка должна содержать только английские буквы, цифры и нижнее подчеркивание.\n"
                                                "Допустимый размер - от 7 до 30 символов.\n\n"
                                                "Попробуйте заново",
                                           reply_markup=await main_menu_bt())
            await state.clear()



@bot_router.message()
async def any_or_answer(message:Message, state: FSMContext):
    channels_checker = await check_channels(message)
    checker = check_user(message.from_user.id)
    check = None
    if message.reply_to_message:
        check = check_reply(message.reply_to_message.message_id)
    if not channels_checker:
        if not checker:
            new_link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
            link_for_db = new_link[new_link.index("=")+1:]
            add_user(message.from_user.id, link_for_db)
            await message.bot.send_message(chat_id=message.from_user.id, text="", reply_markup=await main_menu_bt())
    elif not checker:
        new_link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
        link_for_db = new_link[new_link.index("=") + 1:]
        add_user(message.from_user.id, link_for_db)

        await message.bot.send_message(chat_id=message.from_user.id,
                                       text=f"🚀 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n"
                                            f"Твоя личная ссылка:\n👉{new_link}\n\n"
                                            f"Размести эту ссылку ☝️ в своём профиле Telegram/Instagram/TikTok или "
                                            f"других соц сетях, чтобы начать получать сообщения 💬", parse_mode="html",
                                       reply_markup=await main_menu_bt())
    elif check:
        to_id = check[0]
        to_message = check[1]
        caption = ""
        try:
            if message.caption:
                caption = message.caption
            if message.voice:
                await message.bot.copy_message(chat_id=to_id, from_chat_id=message.from_user.id,
                                               message_id=message.message_id, reply_to_message_id=to_message,
                                               reply_markup=await again_in(message.from_user.id))
                await message.bot.send_message(chat_id=message.from_user.id, text="<b>Твой ответ успешно отправлен</b> 😺",
                                               reply_markup=await main_menu_bt(), parse_mode="html")
                add_answer_statistic(message.from_user.id)
            elif message.video_note or message.sticker or message.text:
                await message.bot.copy_message(chat_id=to_id, from_chat_id=message.from_user.id,
                                               message_id=message.message_id, reply_to_message_id=to_message,
                                               reply_markup=await again_in(message.from_user.id))
                await message.bot.send_message(chat_id=message.from_user.id, text="<b>Твой ответ успешно отправлен</b> 😺",
                                               reply_markup=await main_menu_bt(), parse_mode="html")
                add_answer_statistic(message.from_user.id)
            elif message.video or message.photo or message.document:
                await message.bot.copy_message(chat_id=to_id, from_chat_id=message.from_user.id,
                                               message_id=message.message_id,
                                               caption=caption,
                                               reply_to_message_id=to_message,
                                               reply_markup=await again_in(message.from_user.id))
                await message.bot.send_message(chat_id=message.from_user.id, text="<b>Твой ответ успешно отправлен</b> 😺",
                                               reply_markup=await main_menu_bt(), parse_mode="html")
                add_answer_statistic(message.from_user.id)
            else:
                await message.bot.send_message(message.from_user.id, "️️❗Ошибка. Неподдерживаемый формат",
                                               reply_markup=await main_menu_bt())
        except:
            await message.bot.send_message(message.from_user.id, "️️❗Ошибка. Не удалось отправить ответ",
                                           reply_markup=await main_menu_bt())
    else:
        if message.text == "☕️Поддержать разработчика":
            await message.bot.send_message(chat_id=message.from_user.id, text="Если вам нравится наш бот, вы можете "
                                                                              "поддержать нас звездами⭐️",
                                           reply_markup=await payment_amount_keyboard())
        elif message.text == "👋Изменить приветствие":
            await message.bot.send_message(chat_id=message.from_user.id, text="👋Вы можете установить приветствие. "
                                                                              "Каждый, кто перейдёт по вашей ссылке, "
                                                                              "увидит его.\n"
                                                                              "Приветствие не может быть короче 5 и длиннее 300 символов.",
                                           reply_markup= await greeting_in())
            await state.set_state(Links.change_greeting)
        elif message.text == "📛Изменить ссылку":
            link = await create_start_link(message.bot, get_user_link(message.from_user.id))
            await message.bot.send_message(chat_id=message.from_user.id, text=f"Сейчас ваша ссылка для получения анонимных сообщений выглядит так:\n"
                                                                              f"<code>{link}</code>\n\n"
                                                                              f"📛Новая ссылка должна содержать только английские буквы, цифры и нижнее подчеркивание.\n\n"
                                                                              f"❗ Обратите внимание, что при смене ссылки, старая ссылка перестанет быть активной!",
                                           parse_mode="html", reply_markup=await link_in())
            await state.set_state(Links.change_link)
        elif message.text == "🚀Начать":
            await state.clear()
            link = await create_start_link(message.bot, get_user_link(message.from_user.id))
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text=f"🚀 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n"
                                                f"Твоя личная ссылка:\n👉{link}\n\n"
                                                f"Размести эту ссылку ☝️ в своём профиле Telegram/Instagram/TikTok или "
                                                f"других соц сетях, чтобы начать получать сообщения 💬",
                                           parse_mode="html",
                                           reply_markup=await main_menu_bt())
        elif message.text == "⭐️Ваша статистика":
            statistic = get_all_statistic(message.from_user.id)
            bot_info = await create_start_link(message.bot, str(message.from_user.id))
            bot_cor = bot_info.replace("https://t.me/", "")
            index = bot_cor.index("?")
            bot_username = bot_cor[:index]


            await message.bot.send_message(chat_id=message.from_user.id,
                                           text=f"Ваша статистика:\n\n"
                                                f"💬 Сообщений сегодня: {statistic.get("messages_today")}\n"
                                                f"↩️ Ответов сегодня: {statistic.get("answers_today")}\n"
                                                f"👁‍🗨 Переходов по ссылке сегодня: {statistic.get("links_today")}\n"
                                                f"⭐️ Популярность сегодня: {statistic.get("position_today")} место\n\n"
                                                f"💬 Сообщений за всё время: {statistic.get("messages_overall")}\n"
                                                f"↩️ Ответов за всё время: {statistic.get("answers_overall")}\n"
                                                f"👁‍🗨 Переходов по ссылке за всё время: {statistic.get("links_overall")}\n"
                                                f"⭐️ Популярность за всё время: {statistic.get("position_overall")} место\n\n"
                                                f"Для повышения ⭐️ популярности необходимо увеличить "
                                                f"количество переходов по вашей ссылке.\n\n"
                                                f"@{bot_username}",
                                           parse_mode="html", reply_markup=await main_menu_bt())

        else:
            link = await create_start_link(message.bot, get_user_link(message.from_user.id))
            await message.bot.send_message(chat_id=message.from_user.id,
                                           text=f"🚀 <b>Начни получать анонимные сообщения прямо сейчас!</b>\n\n"
                                                f"Твоя личная ссылка:\n👉{link}\n\n"
                                                f"Размести эту ссылку ☝️ в своём профиле Telegram/Instagram/TikTok или "
                                                f"других соц сетях, чтобы начать получать сообщения 💬", parse_mode="html",
                                           reply_markup=await main_menu_bt())