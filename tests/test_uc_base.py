import unittest
from tests.test_config import (
    TEST_HTTP_ENDPOINT_URI_V3,
    TEST_KEYSTORE_PW,
    TEST_KEYSTORE_TEST1,
    TEST_KEYSTORE_UC,
    TEST_KEYSTORE_PROVIDER,
    TEST_KEYSTORE_CUSTOMER
)
from time import sleep
from os import path
# from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import (
    DeployTransactionBuilder,
)
from iconsdk.signed_transaction import SignedTransaction


class TestUcBase(unittest.TestCase):
    _scoreAddrOfContractRegistry = ''
    _scoreAddrOfStoreAgentProxy = ''
    _scoreAddrOfOrderAgentProxy = ''
    _scoreAddrOfStoreAgent = ''
    _scoreAddrOfOrderAgent = ''

    @classmethod
    def setUpClass(self):
        self._currentDirPath = path.abspath(path.dirname(__file__))
        self._walletOfTest1 = KeyWallet.load(f'{self._currentDirPath}/.keystore/{TEST_KEYSTORE_TEST1}', 'test1_Account')
        self._walletOfUc = KeyWallet.load(f'{self._currentDirPath}/.keystore/{TEST_KEYSTORE_UC}', TEST_KEYSTORE_PW)
        self._walletOfProvider = KeyWallet.load(f'{self._currentDirPath}/.keystore/{TEST_KEYSTORE_PROVIDER}', TEST_KEYSTORE_PW)
        self._walletOfCustomer = KeyWallet.load(f'{self._currentDirPath}/.keystore/{TEST_KEYSTORE_CUSTOMER}', TEST_KEYSTORE_PW)
        self._iconService = IconService(HTTPProvider(TEST_HTTP_ENDPOINT_URI_V3))

    def setUp(self):
        self._scoreAddrOfContractRegistry = self.__class__._scoreAddrOfContractRegistry
        self._scoreAddrOfOrderAgentProxy = self.__class__._scoreAddrOfOrderAgentProxy
        self._scoreAddrOfStoreAgentProxy = self.__class__._scoreAddrOfStoreAgentProxy
        self._scoreAddrOfOrderAgent = self.__class__._scoreAddrOfOrderAgent
        self._scoreAddrOfStoreAgent = self.__class__._scoreAddrOfStoreAgent

    def _deploy(self, _installContentBytes: bytes, _params: object) -> str:
        transaction = DeployTransactionBuilder()\
            .from_(self._walletOfUc.get_address())\
            .to('cx0000000000000000000000000000000000000000')\
            .step_limit(1000000000)\
            .nid(3)\
            .nonce(100)\
            .content_type('application/zip')\
            .content(_installContentBytes)\
            .params(_params)\
            .build()

        signedTransaction = SignedTransaction(transaction, self._walletOfUc)
        txHash = self._iconService.send_transaction(signedTransaction)

        scoreAddr = ''
        for i in range(1, 11):
            sleep(1)
            try:
                txResult = self._iconService.get_transaction_result(txHash)
            except:
                continue
            else:
                break

        self.assertNotEqual(txResult, None)
        scoreAddr = txResult['scoreAddress']
        self.assertNotEqual(scoreAddr, '')
        return scoreAddr

    def _sendTransaction(self, _transaction: object, _wallet: object) -> object:
        signedTransaction = SignedTransaction(_transaction, _wallet)
        txHash = self._iconService.send_transaction(signedTransaction)

        txResult = None
        for i in range(1, 11):
            sleep(1)
            try:
                txResult = self._iconService.get_transaction_result(txHash)
            except:
                continue
            else:
                break

        self.assertNotEqual(txResult, None)
        self.assertEqual(txResult['status'], 0x1)
        return txResult

    def _sendCall(self, _call: object) -> object:
        return self._iconService.call(_call)

    def _getBalance(self, _owner: str) -> int:
        return self._iconService.get_balance(_owner)


if __name__ == '__main__':
    unittest.main()
