from iconservice import *
import json

TAG = 'UcOrderAgentProxy'


class UcContractRegistryInterface(InterfaceScore):
    @interface
    def getCount(self) -> int:
        pass

    @interface
    def getAddressByName(self, _name: str, _version: int=0) -> Address:
        pass


class UcStoreAgentProxyInterface(InterfaceScore):
    @interface
    def getCount(self) -> int:
        pass

    @interface
    def changeItemOwner(self, _index: int, _owner: Address) -> None:
        pass


class UcOrderAgentInterface(InterfaceScore):
    @interface
    def getSchema(self) -> str:
        pass

    @interface
    def propose(self, _sender: Address, _itemId: int, _value: int) -> str:
        pass

    @interface
    def cancel(self, _sender: Address, _order: str) -> str:
        pass

    @interface
    def accept(self, _sender: Address, _order: str, _value: int) -> str:
        pass

    @interface
    def reject(self, _sender: Address, _order: str) -> str:
        pass

    @interface
    def finalize(self, _sender: Address, _order: str) -> str:
        pass


class UcOrderAgentProxy(IconScoreBase):

    _ORDERS = 'orders'
    _CONTRACT_REGISTRY = 'contract_registry'
    _STORE_AGENT_PROXY = 'store_agent_proxy'
    _BALANCES = 'balances'
    _BALANCES_IN_PROGRESS = 'balances_in_progress'
    _NAME_ORDER_AGENT = 'OrderAgent'
    _SCHEMA_ITEM_ID = 'itemId'
    _SCHEMA_VALUE = 'value'
    _SCHEMA_OWNER = 'owner'
    _SCHEMA_ITEM_OWNER = 'itemOwner'

    @eventlog(indexed=2)
    def IcxWithdrawed(self, _to: Address, _value: int):
        pass

    @eventlog(indexed=2)
    def IcxReserved(self, _from: Address, _value: int):
        pass

    @eventlog(indexed=1)
    def OrderProposed(self, _index: int):
        pass

    @eventlog(indexed=1)
    def OrderCanceled(self, _index: int):
        pass

    @eventlog(indexed=1)
    def OrderAccepted(self, _index: int):
        pass

    @eventlog(indexed=1)
    def OrderRejected(self, _index: int):
        pass

    @eventlog(indexed=1)
    def OrderFinalized(self, _index: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._orders = ArrayDB(self._ORDERS, db, value_type=str)
        self._contractRegistry = VarDB(self._CONTRACT_REGISTRY, db, value_type=Address)
        self._storeAgentProxy = VarDB(self._STORE_AGENT_PROXY, db, value_type=Address)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._balancesInProgress = DictDB(self._BALANCES_IN_PROGRESS, db, value_type=int)

    def on_install(self, _contractRegistry: Address, _storeAgentProxy: Address) -> None:
        super().on_install()

        if self.get_owner(_contractRegistry) != self.msg.sender:
            self.revert('No permission for contractRegistry')

        contractRegistryScore = self.create_interface_score(_contractRegistry, UcContractRegistryInterface)
        contractRegistryScore.getCount()

        if self.get_owner(_storeAgentProxy) != self.msg.sender:
            self.revert('No permission for storeAgentProxy')

        storeAgentProxyScore = self.create_interface_score(_storeAgentProxy, UcStoreAgentProxyInterface)
        storeAgentProxyScore.getCount()

        self._contractRegistry.set(_contractRegistry)
        self._storeAgentProxy.set(_storeAgentProxy)

    def on_update(self) -> None:
        super().on_update()

    def _getOrderAgentScore(self):
        contractRegistryScore = self.create_interface_score(self._contractRegistry.get(), UcContractRegistryInterface)
        contractAddress = contractRegistryScore.getAddressByName(self._NAME_ORDER_AGENT)
        return self.create_interface_score(contractAddress, UcOrderAgentInterface)

    def _isOutOfRange(self, _index: int) -> bool:
        return _index < 0 or _index >= len(self._orders)

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    @payable
    def fallback(self):
        self._balances[self.msg.sender] += self.msg.value
        self.IcxReserved(self.msg.sender, self.msg.value)

    @external
    def withdraw(self, _value: int) -> None:
        if _value <= 0:
            self.revert('Invalid argument')

        if self._balances[self.msg.sender] < _value:
            self.revert('Not enough balance')

        self._balances[self.msg.sender] -= _value
        # if self.icx.send(self.msg.sender, _value):
        #     self.IcxWithdrawed(self.msg.sender, _value)
        # else:
        #     self._balances[self.msg.sender] += _value
        self.icx.send(self.msg.sender, _value)
        self.IcxWithdrawed(self.msg.sender, _value)

    @external(readonly=True)
    def getSchema(self) -> str:
        return self._getOrderAgentScore().getSchema()

    @external(readonly=True)
    def get(self, _index: int) -> str:
        if self._isOutOfRange(_index):
            self.revert('No such order')

        order = self._orders[_index]
        return order

    @external(readonly=True)
    def getCount(self) -> int:
        return len(self._orders)

    @external
    def propose(self, _itemId: int, _value: int) -> None:
        if _value < 0 or self._balances[self.msg.sender] < _value:
            self.revert(f'Not enough balance: {self.msg.sender}, {self._balances[self.msg.sender]}, {_value}')

        order = self._getOrderAgentScore().propose(self.msg.sender, _itemId, _value)
        if not order:
            self.revert('Internal error')

        orderObj = json.loads(order)
        value = orderObj[self._SCHEMA_VALUE]
        orderOwner = Address.from_string(orderObj[self._SCHEMA_OWNER])

        index = len(self._orders)

        self._balances[orderOwner] -= value
        self._balancesInProgress[orderOwner] += value

        self._orders.put(order)
        self.OrderProposed(index)

    @external
    def cancel(self, _index: int) -> None:
        if self._isOutOfRange(_index):
            self.revert('No such order')

        order = self._getOrderAgentScore().cancel(self.msg.sender, self._orders[_index])
        if not order:
            self.revert('Internal error')

        orderObj = json.loads(order)
        value = orderObj[self._SCHEMA_VALUE]
        orderOwner = Address.from_string(orderObj[self._SCHEMA_OWNER])

        self._balances[orderOwner] += value
        self._balancesInProgress[orderOwner] -= value

        self._orders[_index] = order
        self.OrderCanceled(_index)

    @external
    def accept(self, _index: int, _value: int) -> None:
        if _value < 0 or self._balances[self.msg.sender] < _value:
            self.revert('Not enough balance')

        if self._isOutOfRange(_index):
            self.revert('No such order')

        order = self._getOrderAgentScore().accept(self.msg.sender, self._orders[_index], _value)
        if not order:
            self.revert('Internal error')

        orderObj = json.loads(order)
        value = orderObj[self._SCHEMA_VALUE]
        itemOwner = Address.from_string(orderObj[self._SCHEMA_ITEM_OWNER])

        self._balances[itemOwner] -= _value
        self._balancesInProgress[itemOwner] += _value

        self._orders[_index] = order
        self.OrderAccepted(_index)

    @external
    def reject(self, _index: int) -> None:
        if self._isOutOfRange(_index):
            self.revert('No such order')

        order = self._getOrderAgentScore().reject(self.msg.sender, self._orders[_index])
        if not order:
            self.revert('Internal error')

        orderObj = json.loads(order)
        value = orderObj[self._SCHEMA_VALUE]
        orderOwner = Address.from_string(orderObj[self._SCHEMA_OWNER])

        self._balances[orderOwner] += value
        self._balancesInProgress[orderOwner] -= value

        self._orders[_index] = order
        self.OrderRejected(_index)

    @external
    def finalize(self, _index: int) -> None:
        if self._isOutOfRange(_index):
            self.revert('No such order')

        order = self._getOrderAgentScore().finalize(self.msg.sender, self._orders[_index])
        if not order:
            self.revert('Internal error')

        orderObj = json.loads(order)
        itemId = orderObj[self._SCHEMA_ITEM_ID]
        orderOwner = Address.from_string(orderObj[self._SCHEMA_OWNER])
        value = orderObj[self._SCHEMA_VALUE]
        itemOwner = Address.from_string(orderObj[self._SCHEMA_ITEM_OWNER])

        storeAgentProxyScore = self.create_interface_score(self._storeAgentProxy.get(), UcStoreAgentProxyInterface)
        storeAgentProxyScore.changeItemOwner(itemId, orderOwner)

        self._balancesInProgress[orderOwner] -= value
        self._balancesInProgress[itemOwner] -= value
        self._balances[itemOwner] += value * 2

        self._orders[_index] = order
        self.OrderFinalized(_index)
