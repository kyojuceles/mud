#item.py

class Item:
    def __init__(self, uid: int, item_id: int, name: str):
        self._uid = uid
        self._item_id = item_id
        self._name = name

    def get_uid(self):
        return self._uid

    def get_item_id(self):
        return self._item_id

    def get_name(self):
        return self._name

    