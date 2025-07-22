import os
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
from dotenv import load_dotenv

load_dotenv()


milvus_url = os.getenv("MILVUS_URL")
milvus_user = os.getenv("MILVUS_USER")
milvus_password = os.getenv("MILVUS_PASSWORD")
if not milvus_url:
    raise ValueError("MILVUS_URL environment variable is not set")
client = MilvusClient(uri=milvus_url, token=f"{milvus_user}:{milvus_password}")

# client.create_database(db_name="my_database_23232")
# 打印结果
print(client.list_databases())

client.create_database(db_name="personal")

# 切换数据库
client.switch_database(db_name="personal")

schema = CollectionSchema(
    fields=[
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=100)
    ],
    description="Personal info collection"
)
# 创建集合
client.create_collection(collection_name="personal_info", schema=schema)