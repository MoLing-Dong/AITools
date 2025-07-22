import os
from pymilvus import MilvusClient
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
