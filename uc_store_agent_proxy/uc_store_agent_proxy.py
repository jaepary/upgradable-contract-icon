from iconservice import *
import json

TAG = 'UcStoreAgentProxy'


class UcContractRegistryInterface(InterfaceScore):
    @interface
    def getCount(self) -> int:
        pass

    @interface
    def getAddressByName(self, _name: str, _version: int=0) -> Address:
        pass


class UcStoreAgentInterface(InterfaceScore):
    @interface
    def getSchema(self) -> str:
        pass

    @interface
    def register(self, _sender: Address, _itemName: str, _itemDetails: str) -> str:
        pass

    @interface
    def changeItemOwner(self, _sender: Address, _item: str, _owner: Address) -> str:
        pass

    @interface
    def open(self, _sender: Address, _item: str) -> str:
        pass

    @interface
    def close(self, _sender: Address, _item: str) -> str:
        pass


class UcStoreAgentProxy(IconScoreBase):

    _ITEMS = 'items'
    _CONTRACT_REGISTRY = 'contract_registry'
    _RELATED_CONTRACTS = 'related_contracts'
    _NAME_STORE_AGENT = 'StoreAgent'
    _SCHEMA_OWNER = 'owner'

    @eventlog(indexed=1)
    def ItemRegistered(self, _index: int):
        pass

    @eventlog(indexed=1)
    def ItemOpened(self, _index: int):
        pass

    @eventlog(indexed=1)
    def ItemClosed(self, _index: int):
        pass

    @eventlog(indexed=1)
    def ItemOwnerChanged(self, _index: int):
        pass

    @eventlog(indexed=1)
    def ContractRelated(self, _contract: Address):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._items = ArrayDB(self._ITEMS, db, value_type=str)
        self._contractRegistry = VarDB(self._CONTRACT_REGISTRY, db, value_type=Address)
        self._relatedContracts = DictDB(self._RELATED_CONTRACTS, db, value_type=str)

    def on_install(self, _contractRegistry: Address) -> None:
        super().on_install()

        if self.get_owner(_contractRegistry) != self.msg.sender:
            self.revert('No permission for contractRegistry')

        contractRegistryScore = self.create_interface_score(_contractRegistry, UcContractRegistryInterface)
        contractRegistryScore.getCount()

        self._contractRegistry.set(_contractRegistry)

    def on_update(self) -> None:
        super().on_update()

    def _getStoreAgentScore(self):
        contractRegistryScore = self.create_interface_score(self._contractRegistry.get(), UcContractRegistryInterface)
        contractAddress = contractRegistryScore.getAddressByName(self._NAME_STORE_AGENT)
        return self.create_interface_score(contractAddress, UcStoreAgentInterface)

    def _isOutOfRange(self, _index: int) -> bool:
        return _index < 0 or _index >= len(self._items)

    def _isContractOwner(self) -> bool:
        return self.msg.sender == self.owner

    def _isRelatedContract(self) -> bool:
        return True if self._relatedContracts[str(self.msg.sender)] else False

    @external(readonly=True)
    def getSchema(self) -> str:
        return self._getStoreAgentScore().getSchema()

    @external(readonly=True)
    def get(self, _index: int) -> str:
        if self._isOutOfRange(_index):
            self.revert('No such item')

        item = self._items[_index]
        return item

    @external(readonly=True)
    def getCount(self) -> int:
        return len(self._items)

    @external(readonly=True)
    def getItemOwner(self, _index: int) -> Address:
        if self._isOutOfRange(_index):
            self.revert('No such item')

        itemObj = json.loads(self._items[_index])
        return Address.from_string(itemObj[self._SCHEMA_OWNER])

    @external
    def register(self, _itemName: str, _itemDetails: str) -> None:
        item = self._getStoreAgentScore().register(self.msg.sender, _itemName, _itemDetails)
        if not item:
            self.revert('Internal error')

        index = len(self._items)

        self._items.put(item)
        self.ItemRegistered(index)

    @external
    def open(self, _index: int) -> None:
        if self._isOutOfRange(_index):
            self.revert('No such item')

        item = self._getStoreAgentScore().open(self.msg.sender, self._items[_index])
        if not item:
            self.revert('Internal error')

        self._items[_index] = item
        self.ItemOpened(_index)

    @external
    def close(self, _index: int) -> None:
        if self._isOutOfRange(_index):
            self.revert('No such item')

        item = self._getStoreAgentScore().close(self.msg.sender, self._items[_index])
        if not item:
            self.revert('Internal error')

        self._items[_index] = item
        self.ItemClosed(_index)

    @external
    def changeItemOwner(self, _index: int, _owner: Address) -> None:
        if not self._isRelatedContract():
            self.revert('No permission')

        if self._isOutOfRange(_index):
            self.revert('No such item')

        item = self._getStoreAgentScore().changeItemOwner(self.msg.sender, self._items[_index], _owner)
        if not item:
            self.revert('Internal error')

        self._items[_index] = item
        self.ItemOwnerChanged(_index)

    @external
    def relateTo(self, _contract: Address) -> None:
        if not self._isContractOwner():
            self.revert('No permission')

        self._relatedContracts[str(_contract)] = str(_contract)
        self.ContractRelated(_contract)
