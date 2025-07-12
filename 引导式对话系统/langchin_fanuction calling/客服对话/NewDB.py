"""
使用python连接PostGreSql数据库，根据用户在对话过程中的业务槽位的新增与更新
"""
import asyncio
import json

import asyncpg
import datetime
import logging
from config import consult_config

# slot_info_dict={}
# slot_info_dict[]

consult_config = consult_config()
async def connect():
    conn = await asyncpg.connect(user=consult_config.user,
                                 password=consult_config.password,
                                 database=consult_config.dbname,
                                 host=consult_config.db_host,
                                 port=consult_config.db_port)
    return conn
async def close_db(conn):
    await conn.close()
async def ensure_connection(conn):
    if conn is None or conn.is_closed():
        # print("连接不存在或已关闭，正在重新连接...")
        conn = await connect()
    # else:
    #     print("连接已经存在，无需重新连接。")
    return conn
async def insert_SlotInfo(conn, table_name, data_to_insert):
    """
    异步插入数据到 slot_info 表
    """
    insert_query = f"""
    INSERT INTO {table_name} (group_id, slot_info_dict,created_time,type)
    VALUES ($1, $2,$3,$4);
    """
    print(data_to_insert)
    try:
        # async with db_client.pool.acquire() as conn:
        await conn.execute(insert_query, *data_to_insert)
        # print.info("插入数据成功")
    except Exception as e:
        print(f"插入数据到 slot_info 表时发生错误: {e}")
async def Read_SlotInfo(conn, table_name, group_id):
    """
    异步读取 slot_info 表中指定 group_id 的数据
    :return: 查询结果，如果发生错误则返回空列表
    """
    select_query = f"""SELECT * FROM {table_name} WHERE group_id = $1; 
    """
    try:
        # async with db_client.pool.acquire() as conn:
        result = await conn.fetch(select_query, group_id)
        return result
    except Exception as e:
        print(f"读取 slot_info 表数据时发生错误: {e}")
        return []
async def DEL_SlotInfo(conn, table_name, group_id):
    """
    异步读取 slot_info 表中指定 group_id 的数据
    :return: 查询结果，如果发生错误则返回空列表
    """
    select_query = f"""delete  FROM {table_name} WHERE group_id = $1; 
    """
    try:
        # async with db_client.pool.acquire() as conn:
        result = await conn.fetch(select_query, group_id)
        return result
    except Exception as e:
        print(f"读取 slot_info 表数据时发生错误: {e}")
        return []
async def update_SlotInfo(conn, table_name, group_id, slot_info_dict, created_time):
    """
    异步更新 slot_info 表中的数据
    """
    update_query = f"""
    UPDATE {table_name} SET slot_info_dict = $2, created_time = $3
    WHERE group_id = $1;
    """
    try:
        # async with db_client.pool.acquire() as conn:
        await conn.execute(update_query, group_id, slot_info_dict, created_time)
        # print("槽位更新成功")
    except Exception as e:
        print(f"更新 slot_info 表数据时发生错误: {e}")

data_to_insert = ('1', '{"slot1": "info1", "slot2": "info2"}', '2025-07-08 20:00:00', 'example_type')
async def main():
    conn=await connect()
    result=await Read_SlotInfo(conn,"slot_info_table","12")
    a=json.loads(result[0]['slot_info_dict'])
    for k,v in a.items():
        for key,val in v.items():
            print(key,val)
        # for key,val in v:
        #     print(key,val)
    return result
if __name__ == "__main__":
    asyncio.run(main())


# 数据库 创建槽位表:
# CREATE TABLE IF NOT EXISTS slot_info_table (
#                 group_id VARCHAR(255) PRIMARY KEY,
#                 slot_info_dict TEXT,
#                 created_time VARCHAR(255) NOT NULL,
#                 type TEXT
#             );