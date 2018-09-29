import unittest
from tests.test_config import (
    TEST_CONTENT_HEX_CONTRACT_REGISTRY,
    TEST_CONTENT_HEX_STORE_AGENT
)
# from os import path
# from iconsdk.libs.in_memory_zip import gen_deploy_data_content
import sys
import json
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder
)
from tests.test_uc_base import TestUcBase


class TestUcContractRegistry(TestUcBase):
    _scoreAddrOfStoreAgent2 = ''

    def setUp(self):
        self._scoreAddrOfStoreAgent2 = self.__class__._scoreAddrOfStoreAgent2

    def test_001_deploy(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_contract_registry')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_CONTRACT_REGISTRY

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}

        self.__class__._scoreAddrOfContractRegistry = self._deploy(installContentBytes, params)

    def test_002_deploy_store_agent(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_store_agent_1')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}

        self.__class__._scoreAddrOfStoreAgent = self._deploy(installContentBytes, params)

    def test_003_register(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('register')\
            .params({'_contractAddress': self._scoreAddrOfStoreAgent})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfUc)

    def test_004_get_count(self):
        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1')

    def test_005_get_address_by_name(self):
        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getAddressByName')\
            .params({'_contractName': 'StoreAgent'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, self._scoreAddrOfStoreAgent)

    def test_006_get(self):
        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['address'], self._scoreAddrOfStoreAgent)
        self.assertEqual(json.loads(callResult)['version'], 1)

    def test_007_deploy_store_agent_2(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_store_agent_1')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}

        self.__class__._scoreAddrOfStoreAgent2 = self._deploy(installContentBytes, params)

    def test_008_upgrade(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('upgrade')\
            .params({'_contractAddress': self._scoreAddrOfStoreAgent2})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfUc)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1')

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getAddressByName')\
            .params({'_contractName': 'StoreAgent'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, self._scoreAddrOfStoreAgent2)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getAddressByName')\
            .params({'_contractName': 'StoreAgent', '_version': '0x1'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, self._scoreAddrOfStoreAgent)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['address'], self._scoreAddrOfStoreAgent2)
        self.assertEqual(json.loads(callResult)['version'], 2)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('get')\
            .params({'_index': '0x0', '_version': '0x1'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['address'], self._scoreAddrOfStoreAgent)
        self.assertEqual(json.loads(callResult)['version'], 1)

    def test_009_downgrade(self):
        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getLatestVersion')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x2')

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('downgrade')\
            .params({'_index': '0x0', '_version': '0x1'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfUc)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['address'], self._scoreAddrOfStoreAgent)
        self.assertEqual(json.loads(callResult)['version'], 1)

        call = CallBuilder().from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .method('getLatestVersion')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x2')


if __name__ == '__main__':
    unittest.main()
