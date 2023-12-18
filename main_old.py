import asyncio
import os
from threading import Thread

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.markdown import hbold, hitalic, hlink
from pyrogram import Client

session = { 
    "nik_work" : {
        'api_id' : 16870143,
        'api_hash' : "7c82583b66a59408828d897c149da5df",
    },
    "rusyk_lev" : {
        'api_id' : 29768044,
        'api_hash' : "ceb27266295977ebe4ce320a90ed4c2f",
    },
}
#ADMIN = 515551867
ADMIN = 5693541259
TOKEN = "6605690741:AAGCR2CWPFesB7-N09yta2S2DxTIkuyYAso"

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

choise_acc = []
#choise_acc = ['rusyk_lev', 'nik_work']
user_to_send = []
#user_to_send = {'lexa_minimum': 515551867, 'larhatdreen': 492999470}
sending_mes = {'mes' : None}
#sending_mes = {'mes': 'Привет от ботика тебе)'}
log = {'log' : None}

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if message.from_user.id == ADMIN:
        accounts = await get_accounts()
        builder = InlineKeyboardBuilder()
        for acc in accounts:
            builder.button(text=acc, callback_data=acc)

        builder.button(text="Далее", callback_data="next step")
        builder.adjust(1)
        await message.answer('Выберите аккаунт с которого будем рассылать', reply_markup=builder.as_markup())

@dp.message()
async def send_text(message: Message):
    if message.from_user.id == ADMIN:
        if log['log'] == 'username':
            user_to_send.append(message.text)
            text = 'Username добавлен в рассылку, добавьте еще или продолжите' 
            builder = InlineKeyboardBuilder()
            builder.button(text="Добавить еще", callback_data="next user")
            builder.button(text="Продолжить", callback_data="next text")
            builder.adjust(1)
            log['log'] = None
            await message.answer(text, reply_markup=builder.as_markup())

        elif log['log'] == 'mes_text':
            sending_mes['mes'] = message.text
            text = 'Все поля заполены, после нажатия продолжить, будет выполнена подготовка к рассылке'
            builder = InlineKeyboardBuilder()
            builder.button(text="Продолжить", callback_data="next prepare")
            builder.adjust(1)
            await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query()
async def callbacks_num(callback: types.CallbackQuery):
    data = callback.data.split(' ')
    len_data = len(callback.data.split(' '))
    
    if len_data == 1:
        accounts = await get_accounts()
        builder = InlineKeyboardBuilder()
        for acc in accounts:
            if acc == data[0]:
                builder.button(text=f'{acc}✅', callback_data=f'true {acc}')
                choise_acc.append(acc)
            elif acc in choise_acc:
                builder.button(text=f'{acc}✅', callback_data=f'true {acc}')
            else:
                builder.button(text=acc, callback_data=acc)

        builder.button(text="Далее", callback_data="next user")
        builder.adjust(1)
        await callback.message.edit_reply_markup(reply_markup=builder.as_markup())

    elif len_data == 2:
        if data[0] == 'true':
            accounts = await get_accounts()
            builder = InlineKeyboardBuilder()
            for acc in accounts:
                if acc == data[1]:
                    builder.button(text=f'{acc}', callback_data=acc)
                    choise_acc.remove(acc)
                elif acc in choise_acc:
                    builder.button(text=f'{acc}✅', callback_data=f'true {acc}')
                else:
                    builder.button(text=acc, callback_data=acc)

            builder.button(text="Далее", callback_data="next user")
            builder.adjust(1)
            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        
        elif data[0] == 'next':
            if data[1] == 'user':
                if len(choise_acc) == 0:
                    accounts = await get_accounts()
                    builder = InlineKeyboardBuilder()
                    for acc in accounts:
                        builder.button(text=acc, callback_data=acc)

                    builder.button(text="Далее", callback_data="next step")
                    builder.adjust(1)
                    await callback.message.edit_text(text='Вы не выбрали аккаунт!', reply_markup=builder.as_markup())
                
                else:
                    text = 'Отправьте username для отправки сообщения'
                    log['log'] = 'username'
                    await callback.message.edit_text(text=text)

            elif data[1] == 'text':
                text = 'Отправьте текст для отправки отправки рассылки'
                log['log'] = 'mes_text'
                await callback.message.edit_text(text=text)

            elif data[1] == 'prepare':
                await callback.message.edit_text('Ожидайте, подготовливаем все для рассылки')
                #await prepare_spam()
                text = f"{hbold('Настройки для рассылки:')}\nОтправку выполняем с:\n"
                for acc in choise_acc:
                    text += f"{hitalic(f'@{acc}')}\n"
                text += "\nПосле проверки отправленных user_name подтвердили:\n"
                for user in user_to_send:
                    text += f"{hitalic(f'@{user}')}\n"
                text += f"\nТекст рассылки:\n{sending_mes['mes']}"
                builder = InlineKeyboardBuilder()
                builder.button(text="Начать рассылку", callback_data="start spam")
                builder.adjust(1)
                await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
        
        elif data[0] == 'start':
            if data[1] == 'spam':
                await callback.message.edit_text(text=f"Начинаем рассылку")
                new_thread = Thread(target=spam)
                new_thread.start()
                new_thread.join()
                choise_acc.clear()
                user_to_send.clear()
                sending_mes['mes'] = None
                log['log'] = None
                await callback.message.edit_text(text=f"Рассылка закончена!")
                accounts = await get_accounts()
                builder = InlineKeyboardBuilder()
                for acc in accounts:
                    builder.button(text=acc, callback_data=acc)

                builder.button(text="Далее", callback_data="next step")
                builder.adjust(1)
                await callback.message.answer('Выберите аккаунт с которого будем рыссылкать', reply_markup=builder.as_markup())

def spam():
    asyncio.run(spamming())

async def spamming() -> None:
    for ses in session:
        app = Client(ses, session[ses]['api_id'], session[ses]['api_hash'])
        await app.start()
        for user in user_to_send:
            try:
                await app.send_message(f'@{user}', sending_mes['mes'])
            except:
                pass

async def prepare_spam() -> None:
    for ses in session:
        app = Client(ses, session[ses]['api_id'], session[ses]['api_hash'])
        await app.start()
        contacts = await app.get_contacts()
        for user in user_to_send:
            for contact in contacts:
                if contact.username == user:
                    user_to_send[user] = contact.id   
                         

async def get_accounts() -> list:
    accounts = []
 
    for file in os.listdir(os.path.abspath(os.curdir)):
        if file.endswith(".session"):
            accounts.append(file.replace('.session', ''))
 
    return accounts

async def start() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start())
