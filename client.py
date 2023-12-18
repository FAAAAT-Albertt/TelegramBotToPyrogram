import asyncio
import json
import aiofiles

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import PeerIdInvalid, SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid
from pyrogram.errors.exceptions.flood_420 import FloodWait

import database
from config import APP_ID, APP_HASH
import datetime


async def get_chats(tg_id, all_chat: bool):
    try:
        async with aiofiles.open(f"chat_{tg_id}.json", 'r') as file:
            content = await file.read()
        chats = json.loads(content)
    except:
        user_data = await database.get_user(tg_id)
        if user_data['password'] == 'None':
            app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/')
        else:
            app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/', password=user_data['password'])
        try:
            await app.connect()
            if all_chat:
                chats = await _get_chats_internal(app)
            else:
                chats = await asyncio.wait_for(_get_chats_internal(app), timeout=1800)

            file_name = f"chat_{tg_id}.json"
            async with aiofiles.open(file_name, 'w+') as f:
                await f.write(json.dumps(chats))
        
        except asyncio.TimeoutError:
            await _save_chats_partial(tg_id, chats)
    # finally:
    #     await app.disconnect()
    

async def _get_chats_internal(app):
    chats = []
    contacts = await app.get_contacts()
    async for dialog in app.get_dialogs():
        chat = dialog.chat
        if chat.type == ChatType.PRIVATE and not chat.id == 777000:
            phone = await find_phone(contacts, chat.id)
            # photo_id = await find_photo(contacts, chat.id, app)
            messages = []
            index = 0
            async for message in app.get_chat_history(chat.id):
                if index > 20:
                    break
                else:
                    messages.append(message)
                index += 1
            verified = await verif_messages(messages, chat.id, 1)
            
            if not verified:
                username = chat.username
                if not phone is None and not username is None:
                    verified = await verif_messages(messages, chat.id, 2)
                else:
                    verified = False

            if not verified:
                verified = await find_mutual_contact(contacts, chat.id)

            if chat.last_name is None and chat.username is None:
                name = chat.first_name
            elif not chat.last_name is None and chat.username is None:
                name = chat.first_name + ' ' + chat.last_name
            elif chat.last_name is None and not chat.username is None:
                name = chat.first_name + ' @' + chat.username
            elif not chat.last_name is None and not chat.username is None:
                name = chat.first_name + ' ' + chat.last_name + ' @' + chat.username
            last_mes = dialog.top_message.date.strftime("%d.%m.%y %H:%M")
            chats.append({
                'id' : dialog.chat.id,
                'name' : name, 
                'last_mes' : last_mes,
                'verif' : verified,
                # 'photo_id' : photo_id,
            })
    return chats

async def _save_chats_partial(tg_id, chats):
    file_name = f"chat_{tg_id}_partial.json"
    async with aiofiles.open(file_name, 'w+') as f:
       await f.write(json.dumps(chats))

async def find_phone(contacts, contact_id):
    for contact in contacts:
        if contact.id == contact_id:
            return contact.phone_number

async def find_mutual_contact(contacts, contact_id):
    for contact in contacts:
        if contact.id == contact_id:
            return contact.is_mutual_contact
# async def find_photo(contacts, contact_id, app: Client):
#     for contact in contacts:
#         if contact.id == contact_id:
#             if not contact.photo is None:
                
#             try:
#                 return contact.photo.big_file_id
#             except:
#                 return contact.photo

async def verif_messages(messages, contact_id, count):
    index_month = 0
    index_year = 0
    for message in messages:
        if message.from_user.id == contact_id and message.date + datetime.timedelta(days=30) >= datetime.datetime.now():
            index_month += 1
        if message.date + datetime.timedelta(days=365) >= datetime.datetime.now():
            index_year += 1
    
    if count == 1:
        if index_month >= 2 or index_year >= 20:
            return True
        else:
            return False
    elif count == 2:
        if index_month >= 2:
            return True
        else:
            return False

async def first_connect(tg_id):
    try:
        try:
            user_data = await database.get_user(tg_id)
            if user_data['password'] == 'None':
                client = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/')
            else:
                client = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/', password=user_data['password'])

            await client.connect()
            sCode = await client.send_code(user_data['phone'])
            check_code = True
            while check_code:
                code = await database.get_code(tg_id)
                if not code is None:
                    await database.delete_code(tg_id)
                    check_code = False
                await asyncio.sleep(2)
            try:
                try:
                    await client.sign_in(user_data['phone'],sCode.phone_code_hash,code)
                except PhoneCodeInvalid:
                    file_name = f"session/{user_data['user_name']}_false.json"
                    with open(file_name, 'w+') as f:
                        f.write("True")
                    return False
            except SessionPasswordNeeded:
                try:
                    await client.check_password(user_data['password'])
                except PasswordHashInvalid:
                    file_name = f"session/{user_data['user_name']}_false.json"
                    with open(file_name, 'w+') as f:
                        f.write("True")
                    return False
            me = await client.get_me()
            await client.disconnect()
            file_name = f"session/{user_data['user_name']}_true.json"
            with open(file_name, 'w+') as f:
                f.write("True")
            return True
        except FloodWait:
            file_name = f"session/{user_data['user_name']}_flood.json"
            with open(file_name, 'w+') as f:
                f.write("True")
            return False
    except Exception as e:
        print(e)
        file_name = f"session/{user_data['user_name']}_false.json"
        with open(file_name, 'w+') as f:
            f.write("True")
        return False

async def spam_to_chat(tg_id, text):
    user_data = await database.get_user(tg_id)
    file_name = f"send_{tg_id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/')
    await app.connect()
    async for dialog in app.get_dialogs():
        for chat_id in js:
            chat = dialog.chat
            if int(chat_id) == chat.id:
                try:
                    await app.send_message(chat.id, text)
                except PeerIdInvalid:
                    if not chat.username is None:
                        await app.send_message(chat.username, text)
    #await app.disconnect()

async def spam_to_contacts(tg_id, text):
    user_data = await database.get_user(tg_id)
    file_name = f"send_contacts_{tg_id}.json"
    with open(file_name, 'r') as file:
        js = json.loads(file.read())
    app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/')
    await app.connect()
    for contact in js:
        try:
            chat_id = contact['contact_id']
            await app.send_message(int(chat_id), text)
        except Exception as ex:
            print(ex)


async def get_contacts(tg_id):
    user_data = await database.get_user(tg_id)
    if user_data['password'] == 'None':
        app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/')
    else:
        app = Client(user_data['user_name'],APP_ID,APP_HASH, workdir='session/', password=user_data['password'])
    try:
        async with aiofiles.open(f"contacts_{tg_id}.json", 'r') as file:
            content = await file.read()
        contact_json = json.loads(content)
    except:
        try:
            await app.connect()
            contacts = await asyncio.wait_for(app.get_contacts(), timeout=1800)
            contact_json = []
            for contact in contacts:
                try:
                    history = await app.get_chat_history(contact.id, limit=1)
                    last_message = history.messages[0] if history.messages else None
                except Exception as e:
                    last_message = None

                check_symbol = "+" if contact.is_mutual_contact else ""
                contact_json.append({
                        'first_name' : f"{contact.first_name} @{contact.username}",
                        'contact_id': contact.id,
                        'last_mess': last_message,
                        'verif': check_symbol
                    })

            file_name = f"contacts_{tg_id}.json"
            async with aiofiles.open(file_name, 'w+') as f:
                await f.write(json.dumps(contact_json))

        except asyncio.TimeoutError:
            _save_contacts_partial(tg_id, contacts)
    finally:
        #app.disconnect()
        return contact_json
    
async def _save_contacts_partial(tg_id, contacts):
    file_name = f"contacts_{tg_id}_partial.json"
    async with aiofiles.open(file_name, 'w+') as f:
       await f.write(json.dumps(contacts))


if __name__ == '__main__':
    asyncio.run(spam_to_chat(6109259540, "Тест Бота"))