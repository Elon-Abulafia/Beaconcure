from .db_factory import DBFactory
from .db_manager import DBManager

manager_factory = DBFactory()


def register_db_manager(db_type: str):
    def decorator(db_manager_class: DBManager):
        manager_factory.register_manager(db_type, db_manager_class)

        return db_manager_class

    return decorator


from .mongodb import MongoDBManager
