from consts import MONGODB_URI
from pymongo.cursor import Cursor
from data_layer import DBManager, register_db_manager
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


@register_db_manager("mongo")
class MongoDBManager(DBManager):
    def __init__(self, *args, db_name: str = None, **kwargs):
        """The MongoDBManager is responsible for every basic interaction with a predefined mongo server.
        In order to connect to the db the environment parameters: MONGODB_PASSWORD, MONGODB_USER, MONGODB_HOST and
        MONGODB_CLUSTER should be defined to your existing database details.

        Args:
            db_name: The name of the working database, e.g. 'db0'
        """

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
        """A decorator that's responsible for keeping connections to the database at a minimum.
        """

        def wrapper(self, *args, **kwargs):
            self.connect()
            try:
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(e)
                result = None
            finally:
                self.disconnect()

            return result

        return wrapper

    @_query_execution
    def insert(self, collection_name: str, data: list | object) -> bool:
        """Inserts given data into the connected DB instance.

        Args:
            collection_name: The name of the MongoDB collection to be inserted into.
            data: The data that is to be inserted, can be either a list of dictionaries or a single one.

        Returns:
            True if the insertion process was a success, False otherwise.
        """

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
        """Executes mongo find function, used in order to iterate over existing documents in the databse.

        Args:
            collection_name: The name of the MongoDB collection to be searched upon.
            query: The query that is to be executed, e.g. {"$gte": {"x": 1}}
            (will return all the documents where the field "x" is greater than or equal to 1).

        Returns:
            A Cursor object to iterate over the results or None if nothing was returned.

        """

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
    def update(self, collection_name: str, query: object, update_type: str, new_data: object) -> int:
        """Updates given query results with the new data.

        Args:
            collection_name: The name of the MongoDB collection that you wish to update.
            query: The query that is to be executed, e.g. {"$gte": {"x": 1}}.
            update_type: The update function from mongo that is to be used, e.g. "$set".
            new_data: The new data that is to be updated, must be an object that is suitable for mongo.

        Returns:
            The number of updated documents.
        """

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
        """Deletes the results of a given query from the db.

        Args:
            collection_name: The name of the MongoDB collection that you wish to delete from.
            query: The query that is to be executed, e.g. {"$gte": {"x": 1}}.

        Returns:
            How many documents were deleted.
        """

        collection = self.db[collection_name]

        try:
            result = collection.delete_many(query)
            result = result.deleted_count
        except Exception as e:
            print(f"An error has occurred when attempting delete query: {query}.\nError: {e}")
            result = 0

        return result
