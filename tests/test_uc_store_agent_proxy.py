import unittest
from tests.test_config import (
    TEST_CONTENT_HEX_CONTRACT_REGISTRY,
    TEST_CONTENT_HEX_STORE_AGENT_PROXY,
    TEST_CONTENT_HEX_ORDER_AGENT_PROXY,
    TEST_CONTENT_HEX_STORE_AGENT,
    TEST_CONTENT_HEX_ORDER_AGENT
)
# from os import path
# from iconsdk.libs.in_memory_zip import gen_deploy_data_content
import json
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder
)
from tests.test_uc_base import TestUcBase


class TestUcStoreAgentProxy(TestUcBase):
    def test_001_prepare(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_contract_registry')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_CONTRACT_REGISTRY

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}
        self.__class__._scoreAddrOfContractRegistry = self._deploy(installContentBytes, params)
        self._scoreAddrOfContractRegistry = self.__class__._scoreAddrOfContractRegistry

        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_store_agent_1')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}
        self.__class__._scoreAddrOfStoreAgent = self._deploy(installContentBytes, params)
        self._scoreAddrOfStoreAgent = self.__class__._scoreAddrOfStoreAgent

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


    def test_002_deploy(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../'uc_store_agent_proxy)
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT_PROXY

        installContentBytes = bytes.fromhex(installContentHex)
        params = {
            '_contractRegistry': self._scoreAddrOfContractRegistry
        }
        self.__class__._scoreAddrOfStoreAgentProxy = self._deploy(installContentBytes, params)
        self._scoreAddrOfStoreAgentProxy = self.__class__._scoreAddrOfStoreAgentProxy

    def test_003_register(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('register')\
            .params({'_itemName': 'A Used Bycicle', '_itemDetails': 'It\'s been used for 3 years'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'ready')
        self.assertEqual(json.loads(callResult)['owner'], self._walletOfProvider.get_address())

    def test_004_close(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('close')\
            .params({'_index': '0x0'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'not-ready')

    def test_004_open(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('open')\
            .params({'_index': '0x0'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'ready')


if __name__ == '__main__':
    unittest.main()
