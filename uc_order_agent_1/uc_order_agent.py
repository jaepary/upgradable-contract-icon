from iconservice import *
import json

TAG = 'UcOrderAgent'


class UcStoreAgentProxyInterface(InterfaceScore):
    @interface
    def getCount(self) -> int:
        pass

    @interface
    def getItemOwner(self, _index: int) -> Address:
        pass


class UcOrderAgent(IconScoreBase):

    _CONTRACT_NAME = 'OrderAgent'
    _CONTRACT_TYPE = 'order-agent'

    _STORE_AGENT_PROXY = 'store_agent_proxy'

    _SCHEMA_ITEM_ID = 'itemId'
    _SCHEMA_VALUE = 'value'
    _SCHEMA_OWNER = 'owner'
    _SCHEMA_ITEM_OWNER = 'itemOwner'
    _SCHEMA_STATE = 'state'
    _SCHEMA_CREATED_AT = 'createdAt'
    _SCHEMA_UPDATED_AT = 'updatedAt'

    _STATE_PROPOSED = 'proposed'
    _STATE_CANCELED = 'canceled'
    _STATE_ACCEPTED = 'accepted'
    _STATE_REJECTED = 'rejected'
    _STATE_FINALIZED = 'finalized'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._schema = {
            'type': 'object',
            'required': ['itemId', 'value', 'owner', 'itemOwner', 'state', 'createdAt', 'updatedAt'],
            'properties': {
                'itemId': {'type': 'number', 'minimum': 0},
                'value': {'type': 'number', 'minimum': 0},
                'owner': {'type': 'string', 'minLength': 1},
                'itemOwner': {'type': 'string', 'minLength': 1},
                'state': {'type': 'string', 'enum': ['proposed', 'canceled', 'accepted', 'rejected', 'finalized']},
                'createdAt': {'type': 'number'},
                'updatedAt': {'type': 'number'}
            }
        }

        self._storeAgentProxy = VarDB(self._STORE_AGENT_PROXY, db, value_type=Address)

    def on_install(self, _storeAgentProxy: Address) -> None:
        super().on_install()

        if self.get_owner(_storeAgentProxy) != self.msg.sender:
            self.revert('No permission for storeAgentProxy')

        storeAgentProxyScore = self.create_interface_score(_storeAgentProxy, UcStoreAgentProxyInterface)
        storeAgentProxyScore.getCount()

        self._storeAgentProxy.set(_storeAgentProxy)

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
    def propose(self, _sender: Address, _itemId: int, _value: int) -> str:
        if not _sender or _itemId < 0 or _value < 0:
            self.revert('Invalid argument')

        storeAgentProxyScore = self.create_interface_score(self._storeAgentProxy.get(), UcStoreAgentProxyInterface)
        itemOwner = storeAgentProxyScore.getItemOwner(_itemId)

        orderObj = {}
        orderObj[self._SCHEMA_ITEM_ID] = _itemId
        orderObj[self._SCHEMA_VALUE] = _value
        orderObj[self._SCHEMA_OWNER] = str(_sender)
        orderObj[self._SCHEMA_ITEM_OWNER] = str(itemOwner)
        orderObj[self._SCHEMA_STATE] = self._STATE_PROPOSED
        ts = self.now()
        orderObj[self._SCHEMA_CREATED_AT] = ts
        orderObj[self._SCHEMA_UPDATED_AT] = ts

        return json.dumps(orderObj)

    @external(readonly=True)
    def cancel(self, _sender: Address, _order: str) -> str:
        if not _sender or not _order:
            self.revert('Invalid argument')

        orderObj = json.loads(_order)
        if orderObj[self._SCHEMA_STATE] != self._STATE_PROPOSED:
            self.revert('Invalid state')

        if str(_sender) != orderObj[self._SCHEMA_OWNER]:
            self.revert('No permission')

        orderObj[self._SCHEMA_STATE] = self._STATE_CANCELED
        orderObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(orderObj)

    @external(readonly=True)
    def accept(self, _sender: Address, _order: str, _value: int) -> str:
        if not _sender or not _order:
            self.revert('Invalid argument')

        orderObj = json.loads(_order)
        if orderObj[self._SCHEMA_STATE] != self._STATE_PROPOSED:
            self.revert('Invalid state')

        if str(_sender) != orderObj[self._SCHEMA_ITEM_OWNER]:
            self.revert('No permission')

        if _value != orderObj[self._SCHEMA_VALUE]:
            self.revert('Invalid value')

        orderObj[self._SCHEMA_STATE] = self._STATE_ACCEPTED
        orderObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(orderObj)

    @external(readonly=True)
    def reject(self, _sender: Address, _order: str) -> str:
        if not _sender or not _order:
            self.revert('Invalid argument')

        orderObj = json.loads(_order)
        if orderObj[self._SCHEMA_STATE] != self._STATE_PROPOSED:
            self.revert('Invalid state')

        if str(_sender) != orderObj[self._SCHEMA_ITEM_OWNER]:
            self.revert('No permission')

        orderObj[self._SCHEMA_STATE] = self._STATE_REJECTED
        orderObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(orderObj)

    @external(readonly=True)
    def finalize(self, _sender: Address, _order: str) -> str:
        if not _sender or not _order:
            self.revert('Invalid argument')

        orderObj = json.loads(_order)
        if orderObj[self._SCHEMA_STATE] != self._STATE_ACCEPTED:
            self.revert('Invalid state')

        if str(_sender) != orderObj[self._SCHEMA_OWNER]:
            self.revert('No permission')

        orderObj[self._SCHEMA_STATE] = self._STATE_FINALIZED
        orderObj[self._SCHEMA_UPDATED_AT] = self.now()

        return json.dumps(orderObj)
