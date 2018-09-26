from iconservice import *
import json

TAG = 'UcStoreAgent'


class UcStoreAgent(IconScoreBase):

    _CONTRACT_NAME = 'StoreAgent'
    _CONTRACT_TYPE = 'store-agent'

    _SCHEMA_NAME = 'name'
    _SCHEMA_DETAILS = 'details'
    _SCHEMA_OWNER = 'owner'
    _SCHEMA_STATE = 'state'
    _SCHEMA_CREATED_AT = 'createdAt'
    _SCHEMA_UPDATED_AT = 'updatedAt'

    _STATE_READY = 'ready'
    _STATE_NOT_READY = 'not-ready'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._schema = {
            'type': 'object',
            'required': ['name', 'details', 'owner', 'state', 'createdAt', 'updatedAt'],
            'properties': {
                'name': {'type': 'string', 'minLength': 1},
                'details': {'type': 'string', 'minLength': 1},
                'owner': {'type': 'string', 'minLength': 1},
                'state': {'type': 'string', 'enum': ['ready', 'not-ready']},
                'createdAt': {'type': 'number'},
                'updatedAt': {'type': 'number'}
            }
        }

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def getName(self) -> str:
        return self._CONTRACT_NAME

    @external(readonly=True)
    def getType(self) -> str:
        return self._CONTRACT_TYPE

    @external(readonly=True)
    def getSchema(self) -> str:
        return json.dumps(self._schema)

    @external(readonly=True)
    def register(self, _sender: Address, _itemName: str, _itemDetails: str) -> str:
        if not _sender or not _itemName or not _itemDetails:
            self.revert('Invalid argument')

        itemObj = {}
        itemObj[self._SCHEMA_NAME] = _itemName
        itemObj[self._SCHEMA_DETAILS] = _itemDetails
        itemObj[self._SCHEMA_OWNER] = str(_sender)
        itemObj[self._SCHEMA_STATE] = self._STATE_READY
        ts = self.now()
        itemObj[self._SCHEMA_CREATED_AT] = ts
        itemObj[self._SCHEMA_UPDATED_AT] = ts

        return json.dumps(itemObj)

    @external(readonly=True)
    def changeItemOwner(self, _sender: Address, _item: str, _owner: Address) -> str:
        if not _sender or not _item or not _owner:
            self.revert('Invalid argument')

        itemObj = json.loads(_item)
        itemObj[self._SCHEMA_OWNER] = str(_owner)
        itemObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(itemObj)

    @external(readonly=True)
    def open(self, _sender: Address, _item: str) -> str:
        if not _sender or not _item:
            self.revert('Invalid argument')

        itemObj = json.loads(_item)
        if str(_sender) != itemObj[self._SCHEMA_OWNER]:
            self.revert('No permission')

        itemObj[self._SCHEMA_STATE] = self._STATE_READY
        itemObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(itemObj)

    @external(readonly=True)
    def close(self, _sender: Address, _item: str) -> str:
        if not _sender or not _item:
            self.revert('Invalid argument')

        itemObj = json.loads(_item)
        if str(_sender) != itemObj[self._SCHEMA_OWNER]:
            self.revert('No permission')

        itemObj[self._SCHEMA_STATE] = self._STATE_NOT_READY
        itemObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(itemObj)
