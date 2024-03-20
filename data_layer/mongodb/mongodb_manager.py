from consts import MONGODB_URI
from pymongo.cursor import Cursor
from data_layer import DBManager, register_db_manager
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


@register_db_manager("mongo")
class MongoDBManager(DBManager):
    def __init__(self, *args, db_name: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.client: MongoClient | None = None
        self.db_name: str = db_name
        self.db: Database | None = None

    def connect(self):
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[self.db_name]
        except Exception as e:
            print(f"An error occurred when attempting to connect to db: {e}")

    def disconnect(self):
        self.client.close()

    def _query_execution(func):
        def wrapper(self, *args, **kwargs):
            self.connect()
            result = func(self, *args, **kwargs)
            self.disconnect()

            return result

        return wrapper

    @_query_execution
    def insert(self, collection_name: str, data: list | object) -> bool:
        collection = self.db[collection_name]

        try:
            if isinstance(data, list):
                response = collection.insert_many(data)
            else:
                response = collection.insert_one(data)

            result = response.acknowledged
        except Exception as e:
            print(e)
            result = False

        return result

    @_query_execution
    def find(self, collection_name: str, query: object = None) -> Cursor | None:
        collection = self.db[collection_name]

        try:
            if query is not None:
                result = collection.find(query)
            else:
                result = collection.find()
        except Exception as e:
            print(f"An error has occurred when attempting find query: {query}.\nError: {e}")
            result = None

        return result

    @_query_execution
    def update(self, collection_name: str, query: object, update_type: str, new_data: object):
        collection = self.db[collection_name]

        try:
            result = collection.update_many(query, {update_type: new_data})

            result = result.modified_count
        except Exception as e:
            print(f"An error has occurred when attempting update query: {query}.\nError: {e}")
            result = 0

        return result

    @_query_execution
    def delete(self, collection_name: str, query: object):
        collection = self.db[collection_name]

        try:
            result = collection.delete_many(query)
            result = result.deleted_count
        except Exception as e:
            print(f"An error has occurred when attempting delete query: {query}.\nError: {e}")
            result = 0

        return result
