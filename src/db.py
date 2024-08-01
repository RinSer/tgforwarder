from rocksdb import Options
from rocksdb import ReadOptions
from rocksdb import RocksDB
from rocksdb import WriteOptions

USER_IDS = "~UsersIds~"
DB = RocksDB(db_path="./db/bot_memory", options=Options(create_if_missing=True))


async def get(key):
    return await DB.get(ReadOptions(), str(key))


async def get_receivers(tag):
    receivers = await get(tag)
    if receivers.value:
        return receivers.value.split(",")


async def get_chat_id(alias):
    chat_id = await get(alias)
    if chat_id.value:
        return int(chat_id.value)


async def put(key, value):
    await DB.put(WriteOptions(), str(key), str(value))


async def add_db_user(user_id):
    user_ids = await get(USER_IDS)
    if user_ids.value:
        ids = user_ids.value.split(",")
        if user_id not in ids:
            user_ids = user_ids.value + f",{user_id}"
        else:
            return
    else:
        user_ids = str(user_id)
    await put(USER_IDS, user_ids)


async def get_users():
    user_ids = await get(USER_IDS)
    return [int(user_id) for user_id in user_ids.value.split(",")] if user_ids.value else []
