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


class TestUcOrderAgentProxy(TestUcBase):
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
        # scorePath = path.join(currentDirPath, '../'uc_store_agent_proxy)
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT_PROXY

        installContentBytes = bytes.fromhex(installContentHex)
        params = {
            '_contractRegistry': self._scoreAddrOfContractRegistry
        }
        self.__class__._scoreAddrOfStoreAgentProxy = self._deploy(installContentBytes, params)
        self._scoreAddrOfStoreAgentProxy = self.__class__._scoreAddrOfStoreAgentProxy

        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_store_agent_1')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_STORE_AGENT

        installContentBytes = bytes.fromhex(installContentHex)
        params = {}
        self.__class__._scoreAddrOfStoreAgent = self._deploy(installContentBytes, params)
        self._scoreAddrOfStoreAgent = self.__class__._scoreAddrOfStoreAgent

        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_order_agent_1')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_ORDER_AGENT

        installContentBytes = bytes.fromhex(installContentHex)
        params = {
            '_storeAgentProxy': self._scoreAddrOfStoreAgentProxy
        }
        self.__class__._scoreAddrOfOrderAgent = self._deploy(installContentBytes, params)
        self._scoreAddrOfOrderAgent = self.__class__._scoreAddrOfOrderAgent

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

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfContractRegistry)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('register')\
            .params({'_contractAddress': self._scoreAddrOfOrderAgent})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfUc)

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

    def test_002_deploy(self):
        # currentDirPath = path.abspath(path.dirname(__file__))
        # scorePath = path.join(currentDirPath, '../uc_order_agent_proxy')
        # installContentBytes = gen_deploy_data_content(scorePath)
        installContentHex = TEST_CONTENT_HEX_ORDER_AGENT_PROXY

        installContentBytes = bytes.fromhex(installContentHex)
        params = {
            '_contractRegistry': self._scoreAddrOfContractRegistry,
            '_storeAgentProxy': self._scoreAddrOfStoreAgentProxy
        }
        self.__class__._scoreAddrOfOrderAgentProxy = self._deploy(installContentBytes, params)
        self._scoreAddrOfOrderAgentProxy = self.__class__._scoreAddrOfOrderAgentProxy

    def test_003_relate(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to(self._scoreAddrOfStoreAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('relateTo')\
            .params({'_contract': self._scoreAddrOfOrderAgentProxy})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfUc)

    def test_004_reserve(self):
        transaction = TransactionBuilder()\
            .from_(self._walletOfTest1.get_address())\
            .to(self._walletOfCustomer.get_address())\
            .value(0x1000000000000000000)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfTest1)

        balance = self._getBalance(self._walletOfCustomer.get_address())
        self.assertEqual(balance, 0x1000000000000000000)

        transaction = TransactionBuilder()\
            .from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .value(0x1000000000000000000)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfCustomer)

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfCustomer.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')

        balance = self._getBalance(self._walletOfCustomer.get_address())
        self.assertEqual(balance, 0x0)

        transaction = TransactionBuilder()\
            .from_(self._walletOfTest1.get_address())\
            .to(self._walletOfProvider.get_address())\
            .value(0x1000000000000000000)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfTest1)

        balance = self._getBalance(self._walletOfProvider.get_address())
        self.assertEqual(balance, 0x1000000000000000000)

        transaction = TransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .value(0x1000000000000000000)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')

        balance = self._getBalance(self._walletOfProvider.get_address())
        self.assertEqual(balance, 0x0)

    def test_005_propose(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('propose')\
            .params({'_itemId': '0x0', '_value': '0x1000000000000000000'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfCustomer)

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1')

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'proposed')
        self.assertEqual(json.loads(callResult)['value'], 0x1000000000000000000)

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfCustomer.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

    def test_006_accept(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('accept')\
            .params({'_index': '0x0', '_value': '0x1000000000000000000'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'accepted')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

    def test_007_finalize(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('finalize')\
            .params({'_index': '0x0'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfCustomer)

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x0'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'finalized')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x2000000000000000000')

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfCustomer.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

    def test_008_withdraw(self):
        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('withdraw')\
            .params({'_value': '0x2000000000000000000'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        balance = self._getBalance(self._walletOfProvider.get_address())
        self.assertEqual(balance, 0x2000000000000000000)

        balance = self._getBalance(self._walletOfCustomer.get_address())
        self.assertEqual(balance, 0x0)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

    def test_009_cancel(self):
        balance = self._getBalance(self._walletOfProvider.get_address())
        self.assertEqual(balance, 0x2000000000000000000)

        transaction = TransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .value(0x1000000000000000000)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')

        balance = self._getBalance(self._walletOfProvider.get_address())
        self.assertEqual(balance, 0x1000000000000000000)

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('propose')\
            .params({'_itemId': '0x0', '_value': '0x1000000000000000000'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x2')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x1'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'proposed')
        self.assertEqual(json.loads(callResult)['value'], 0x1000000000000000000)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('cancel')\
            .params({'_index': '0x1'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x1'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'canceled')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')

    def test_010_reject(self):
        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('propose')\
            .params({'_itemId': '0x0', '_value': '0x1000000000000000000'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfProvider)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('getCount')\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x3')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x2'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'proposed')
        self.assertEqual(json.loads(callResult)['value'], 0x1000000000000000000)

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x0')

        transaction = CallTransactionBuilder()\
            .from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .step_limit(100000000)\
            .nid(3)\
            .nonce(100)\
            .method('reject')\
            .params({'_index': '0x2'})\
            .build()

        txResult = self._sendTransaction(transaction, self._walletOfCustomer)

        call = CallBuilder().from_(self._walletOfCustomer.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('get')\
            .params({'_index': '0x2'})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(json.loads(callResult)['state'], 'rejected')

        call = CallBuilder().from_(self._walletOfProvider.get_address())\
            .to(self._scoreAddrOfOrderAgentProxy)\
            .method('balanceOf')\
            .params({'_owner': self._walletOfProvider.get_address()})\
            .build()

        callResult = self._sendCall(call)
        self.assertEqual(callResult, '0x1000000000000000000')


if __name__ == '__main__':
    unittest.main()
