from iconservice import *
import json

TAG = 'UcContractRegistry'


class UcContractInterface(InterfaceScore):
    @interface
    def getName(self) -> str:
        pass

    @interface
    def getType(self) -> str:
        pass


class UcContractRegistry(IconScoreBase):

    _CONTRACTS = 'contracts'
    _CONTRACTS_BY_NAME = 'contracts_by_name'
    _CONTRACTS_BY_NAME_VERSION = 'contracts_by_name_version'

    _SCHEMA_NAME = 'name'
    _SCHEMA_TYPE = 'type'
    _SCHEMA_VERSION = 'version'
    _SCHEMA_ADDRESS = 'address'
    _SCHEMA_UPDATED_AT = 'updatedAt'

    _KEY_SEPARATOR = '::'

    @eventlog(indexed=1)
    def ContractRegistered(self, _index: int):
        pass

    @eventlog(indexed=1)
    def ContractUpdated(self, _index: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._schema = {
            'type': 'object',
            'required': ['name', 'type', 'version', 'address', 'updatedAt'],
            'services': {
                'name': {'type': 'string'},
                'type': {'type': 'string'},
                'version': {'type': 'number', 'minimum': 1},
                'address': {'type': 'string'},
                'updatedAt': {'type': 'number'}
            }
        }

        self._contracts = ArrayDB(self._CONTRACTS, db, value_type=str)
        self._contractsByName = DictDB(self._CONTRACTS_BY_NAME, db, value_type=str)
        self._contractsByNameVersion = DictDB(self._CONTRACTS_BY_NAME_VERSION, db, value_type=str)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    def _isOutOfRange(self, _index: int) -> bool:
        return _index < 0 or _index >= len(self._contracts)

    def _isContractOwner(self) -> bool:
        return self.msg.sender == self.owner

    @external(readonly=True)
    def getSchema(self) -> str:
        return json.dumps(self._schema)

    @external(readonly=True)
    def get(self, _index: int, _version: int=0) -> str:
        if self._isOutOfRange(_index):
            self.revert('No such contract')

        if _version < 0:
            self.revert('Invalid argument')

        if _version == 0:
            return self._contracts[_index]

        contractObj = json.loads(self._contracts[_index])
        contractName = contractObj[self._SCHEMA_NAME]
        contract = self._contractsByNameVersion[contractName + self._KEY_SEPARATOR + str(_version)]
        if not contract:
            self.revert('No such contract version')

        return contract

    @external(readonly=True)
    def getAddressByName(self, _contractName: str, _version: int=0) -> Address:
        if _version < 0:
            self.revert('Invalid argument')

        if _version == 0:
            indexStr = self._contractsByName[_contractName]
            if not indexStr:
                self.revert('No such contract')

            contractObj = json.loads(self._contracts[int(indexStr)])
        else:
            contract = self._contractsByNameVersion[_contractName + self._KEY_SEPARATOR + str(_version)]
            if not contract:
                self.revert('No such contract version')

            contractObj = json.loads(contract)

        return Address.from_string(contractObj[self._SCHEMA_ADDRESS])

    @external(readonly=True)
    def getCount(self) -> int:
        return len(self._contracts)

    @external
    def register(self, _contractAddress: Address) -> None:
        if not self._isContractOwner():
            self.revert('No permission')

        if self.get_owner(_contractAddress) != self.msg.sender:
            self.revert('No permission for contract')

        contractScore = self.create_interface_score(_contractAddress, UcContractInterface)
        contractName = contractScore.getName()
        if not contractName:
            self.revert('Invalid contract name')

        contractType = contractScore.getType()
        if not contractType:
            self.revert('Invalid contract type')

        if self._contractsByName[contractName]:
            self.revert('Already exists')

        version = 1

        contractObj = {}
        contractObj[self._SCHEMA_NAME] = contractName
        contractObj[self._SCHEMA_TYPE] = contractType
        contractObj[self._SCHEMA_VERSION] = version
        contractObj[self._SCHEMA_ADDRESS] = str(_contractAddress)
        contractObj[self._SCHEMA_UPDATED_AT] = self.now()

        index = len(self._contracts)
        self._contracts.put(json.dumps(contractObj))
        self._contractsByName[contractName] = str(index)

        self._contractsByNameVersion[contractName + self._KEY_SEPARATOR + str(version)] = self._contracts[index]
        self.ContractRegistered(index)

    @external
    def update(self, _contractAddress: Address) -> None:
        if not self._isContractOwner():
            self.revert('No permission')

        if self.get_owner(_contractAddress) != self.msg.sender:
            self.revert('No permission for contract')

        contractScore = self.create_interface_score(_contractAddress, UcContractInterface)
        contractName = contractScore.getName()
        if not contractName:
            self.revert('Invalid contract name')

        contractType = contractScore.getType()
        if not contractType:
            self.revert('Invalid contract type')

        indexStr = self._contractsByName[contractName]
        if not indexStr:
            self.revert('No such contract')

        index = int(indexStr)
        contractObj = json.loads(self._contracts[index])
        if contractObj[self._SCHEMA_TYPE] != contractType:
            self.revert('Mismatch contract type')

        if contractObj[self._SCHEMA_ADDRESS] == str(_contractAddress):
            self.revert('Same contract address')

        version = contractObj[self._SCHEMA_VERSION] + 1

        contractObj = {}
        contractObj[self._SCHEMA_NAME] = contractName
        contractObj[self._SCHEMA_TYPE] = contractType
        contractObj[self._SCHEMA_VERSION] = version
        contractObj[self._SCHEMA_ADDRESS] = str(_contractAddress)
        contractObj[self._SCHEMA_UPDATED_AT] = self.now()

        self._contracts[index] = json.dumps(contractObj)
        self._contractsByNameVersion[contractName + self._KEY_SEPARATOR + str(version)] = self._contracts[index]
        self.ContractUpdated(index)
