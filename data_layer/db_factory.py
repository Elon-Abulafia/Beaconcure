from data_layer.db_manager import DBManager


class DBFactory:
    def __init__(self):
        self._managers = {}

    def register_manager(self, db_type: str, db_manager: DBManager):
        self._managers[db_type] = db_manager

    def get_manager(self, db_type: str, *args, **kwargs) -> DBManager:
        if db_type in self._managers:
            return self._managers[db_type](*args, **kwargs)

        raise ValueError(f"Unknown db type: {db_type}")
