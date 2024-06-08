from rocksdb import Options
from rocksdb import ReadOptions
from rocksdb import RocksDB
from rocksdb import WriteOptions

DB = RocksDB(
    db_path="./db/bot_memory", options=Options(create_if_missing=True)
)


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
