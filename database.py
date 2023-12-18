import asyncio
import sqlite3

con = sqlite3.connect("base.db", check_same_thread=False)
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS {}(id, user_name, phone, password)'.format('users'))
con.commit()

cur.execute('CREATE TABLE IF NOT EXISTS {}(id, code)'.format('codes'))
con.commit()

async def insert_user(tg_id, user_name, data_user) -> None:
    insert_query = f'INSERT INTO users VALUES({tg_id},"{user_name}","{data_user["phone"]}","{data_user["password"]}")'
    cur.execute(insert_query)
    con.commit()

async def get_user(tg_id) -> dict:
    select_query = f'SELECT phone, password, user_name FROM users WHERE id = {tg_id}'
    select = cur.execute(select_query).fetchone()
    return {
        'phone' : select[0],
        'password' : select[1],
        'user_name' : select[2]
    }

async def delete_user(tg_id) -> None:
    delete_query = f'DELETE FROM users WHERE id = {tg_id}'
    cur.execute(delete_query)
    con.commit()

async def insert_code(tg_id, code) -> None:
    insert_query = f'INSERT INTO codes VALUES({tg_id},"{code}")'
    cur.execute(insert_query)
    con.commit()

async def get_code(tg_id) -> int:
    select_query = f'SELECT code FROM codes WHERE id = {tg_id}'
    select = cur.execute(select_query).fetchone()
    if select is None:
        return None
    else:
        return select[0]

async def delete_code(tg_id) -> None:
    delete_query = f'DELETE FROM codes WHERE id = {tg_id}'
    cur.execute(delete_query)
    con.commit()

async def clear_user():
    delete_query = f'DELETE FROM users'
    cur.execute(delete_query)
    con.commit()

if __name__ == "__main__":
    #asyncio.run(clear_user())
    asyncio.run(insert_code(492999470, 22646))