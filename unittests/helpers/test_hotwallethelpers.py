#!/usr/bin/env python
import os
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

# Store original password at module load time
import helpers.hotwallethelpers as _hw_module

from helpers.hotwallethelpers import (
    HotWalletDecryptionError,
    HotWalletPasswordRequired,
    get_hot_wallet,
    prompt_decryption_password,
)

_ORIGINAL_HOT_WALLET_PASSWORD = _hw_module.HOT_WALLET_PASSWORD


def setUpModule():
    """Called once before any tests in this module"""


def tearDownModule():
    """Called once after all tests in this module - restore global state"""
    import helpers.hotwallethelpers as hw_module
    hw_module.HOT_WALLET_PASSWORD = _ORIGINAL_HOT_WALLET_PASSWORD


class TestGetHotWallet(unittest.TestCase):
    """Test cases for get_hot_wallet function"""

    def setUp(self):
        """Save original password before each test"""
        import helpers.hotwallethelpers as hw_module
        self._saved_password = hw_module.HOT_WALLET_PASSWORD

    def tearDown(self):
        """Restore original password after each test"""
        import helpers.hotwallethelpers as hw_module
        hw_module.HOT_WALLET_PASSWORD = self._saved_password

    @staticmethod
    def _mock_file(content='encrypted_data'):
        """Create a mock file object suitable for `with open(...) as f`."""
        mock_file = MagicMock()
        mock_file.read.return_value = content
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        return mock_file

    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=False)
    def test_get_hot_wallet_file_not_found(self, mock_isfile, mock_wallet, mock_dir):
        """Test get_hot_wallet returns an empty dict when the wallet file does not exist."""
        import helpers.hotwallethelpers as hw_module
        hw_module.HOT_WALLET_PASSWORD = None

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        result = get_hot_wallet()

        self.assertEqual(result, {})

    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    @patch('helpers.hotwallethelpers.AESCipher')
    @patch('builtins.open', create=True)
    def test_get_hot_wallet_with_global_password(self, mock_open, mock_cipher_class, mock_isfile, mock_wallet, mock_dir):
        """Test get_hot_wallet decrypts using the HOT_WALLET_PASSWORD global."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = 'test_password'

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = '{"mnemonic": ["word1", "word2"], "passphrase": ""}'
        mock_cipher_class.return_value = mock_cipher

        mock_open.return_value = self._mock_file()

        result = get_hot_wallet()

        self.assertEqual(result['mnemonic'], ['word1', 'word2'])
        mock_cipher_class.assert_called_once_with(key='test_password')

    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    @patch('helpers.hotwallethelpers.AESCipher')
    @patch('builtins.open', create=True)
    def test_get_hot_wallet_with_env_password(self, mock_open, mock_cipher_class, mock_isfile, mock_wallet, mock_dir):
        """Test get_hot_wallet decrypts using the SPELLBOOK_WALLET_PASSWORD env var."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = None

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = '{"mnemonic": ["env"], "passphrase": ""}'
        mock_cipher_class.return_value = mock_cipher

        mock_open.return_value = self._mock_file()

        with mock.patch.dict(os.environ, {'SPELLBOOK_WALLET_PASSWORD': 'envpw'}):
            result = get_hot_wallet()

        self.assertEqual(result['mnemonic'], ['env'])
        mock_cipher_class.assert_called_once_with(key='envpw')

    @patch('helpers.hotwallethelpers.get_allow_empty_password', return_value=True)
    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    @patch('helpers.hotwallethelpers.AESCipher')
    @patch('helpers.hotwallethelpers.LOG')
    @patch('builtins.open', create=True)
    def test_get_hot_wallet_allow_empty_password(self, mock_open, mock_log, mock_cipher_class, mock_isfile, mock_wallet, mock_dir, mock_allow_empty):
        """Test get_hot_wallet decrypts with an empty password when allow_empty_password is enabled."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = None

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = '{"mnemonic": ["legacy"], "passphrase": ""}'
        mock_cipher_class.return_value = mock_cipher

        mock_open.return_value = self._mock_file()

        with mock.patch.dict(os.environ):
            os.environ.pop('SPELLBOOK_WALLET_PASSWORD', None)
            result = get_hot_wallet()

        self.assertEqual(result['mnemonic'], ['legacy'])
        mock_cipher_class.assert_called_once_with(key='')
        mock_log.warning.assert_called_once()

    @patch('helpers.hotwallethelpers.get_allow_empty_password', return_value=False)
    @patch('helpers.hotwallethelpers._is_interactive', return_value=False)
    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    def test_get_hot_wallet_non_interactive_no_password(self, mock_isfile, mock_wallet, mock_dir, mock_interactive, mock_allow_empty):
        """Test get_hot_wallet raises HotWalletPasswordRequired when non-interactive and no password."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = None

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        with mock.patch.dict(os.environ):
            os.environ.pop('SPELLBOOK_WALLET_PASSWORD', None)
            with self.assertRaises(HotWalletPasswordRequired):
                get_hot_wallet()

    @patch('helpers.hotwallethelpers.get_allow_empty_password', return_value=False)
    @patch('helpers.hotwallethelpers._is_interactive', return_value=True)
    @patch('helpers.hotwallethelpers.prompt_decryption_password')
    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    @patch('helpers.hotwallethelpers.AESCipher')
    @patch('builtins.open', create=True)
    def test_get_hot_wallet_interactive_prompts(self, mock_open, mock_cipher_class, mock_isfile, mock_wallet, mock_dir, mock_prompt, mock_interactive, mock_allow_empty):
        """Test get_hot_wallet prompts for a password when interactive and no password is available."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = None

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        mock_prompt.return_value = 'prompted_password'

        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = '{"mnemonic": ["prompted"], "passphrase": ""}'
        mock_cipher_class.return_value = mock_cipher

        mock_open.return_value = self._mock_file()

        with mock.patch.dict(os.environ):
            os.environ.pop('SPELLBOOK_WALLET_PASSWORD', None)
            result = get_hot_wallet()

        mock_prompt.assert_called_once()
        self.assertEqual(result['mnemonic'], ['prompted'])
        mock_cipher_class.assert_called_once_with(key='prompted_password')

    @patch('helpers.hotwallethelpers.get_wallet_dir')
    @patch('helpers.hotwallethelpers.get_default_wallet')
    @patch('helpers.hotwallethelpers.os.path.isfile', return_value=True)
    @patch('helpers.hotwallethelpers.AESCipher')
    @patch('builtins.open', create=True)
    def test_get_hot_wallet_invalid_password(self, mock_open, mock_cipher_class, mock_isfile, mock_wallet, mock_dir):
        """Test get_hot_wallet raises HotWalletDecryptionError when decryption fails."""
        import helpers.hotwallethelpers as hw_module

        hw_module.HOT_WALLET_PASSWORD = 'wrong_password'

        mock_dir.return_value = '/tmp/wallets'
        mock_wallet.return_value = 'test_wallet'

        mock_cipher = MagicMock()
        mock_cipher.decrypt.side_effect = ValueError('Decryption failed')
        mock_cipher_class.return_value = mock_cipher

        mock_open.return_value = self._mock_file()

        with self.assertRaises(HotWalletDecryptionError) as context:
            get_hot_wallet()

        self.assertEqual(str(context.exception), 'Invalid password to decrypt hot wallet!')


class TestIsInteractive(unittest.TestCase):
    """Test cases for _is_interactive function"""

    def test_is_interactive_true(self):
        """Test _is_interactive returns True when stdin is a tty."""
        from helpers.hotwallethelpers import _is_interactive
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = True
            self.assertTrue(_is_interactive())

    def test_is_interactive_false(self):
        """Test _is_interactive returns False when stdin is not a tty."""
        from helpers.hotwallethelpers import _is_interactive
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.return_value = False
            self.assertFalse(_is_interactive())

    def test_is_interactive_exception(self):
        """Test _is_interactive returns False when stdin.isatty raises."""
        from helpers.hotwallethelpers import _is_interactive
        with patch('sys.stdin') as mock_stdin:
            mock_stdin.isatty.side_effect = AttributeError('no isatty')
            self.assertFalse(_is_interactive())


class TestPromptDecryptionPassword(unittest.TestCase):
    """Test cases for prompt_decryption_password function"""

    def setUp(self):
        """Save original password before each test"""
        import helpers.hotwallethelpers as hw_module
        self._saved_password = hw_module.HOT_WALLET_PASSWORD

    def tearDown(self):
        """Restore original password after each test"""
        import helpers.hotwallethelpers as hw_module
        hw_module.HOT_WALLET_PASSWORD = self._saved_password

    @patch('helpers.hotwallethelpers.getpass.getpass', return_value='user_password')
    def test_prompt_decryption_password(self, mock_getpass):
        """Test prompt_decryption_password sets the global password and returns it."""
        import helpers.hotwallethelpers as hw_module

        result = prompt_decryption_password()

        self.assertEqual(hw_module.HOT_WALLET_PASSWORD, 'user_password')
        self.assertEqual(result, 'user_password')


class TestGetAddressFromWallet(unittest.TestCase):
    """Test cases for get_address_from_wallet function"""

    @patch('helpers.hotwallethelpers.get_xpub_key_from_wallet')
    @patch('helpers.hotwallethelpers.get_address_from_xpub')
    def test_get_address_from_wallet(self, mock_get_addr, mock_get_xpub):
        """Test get_address_from_wallet function"""
        from helpers.hotwallethelpers import get_address_from_wallet

        mock_get_xpub.return_value = 'xpub_key'
        mock_get_addr.return_value = '1BitcoinAddress'

        result = get_address_from_wallet(account=0, index=0)

        self.assertEqual(result, '1BitcoinAddress')
        mock_get_xpub.assert_called_once_with(0)
        mock_get_addr.assert_called_once_with(xpub='xpub_key', i=0)


class TestGetXpubKeyFromWallet(unittest.TestCase):
    """Test cases for get_xpub_key_from_wallet function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpub_key')
    def test_get_xpub_key_from_wallet(self, mock_get_xpub, mock_hot_wallet):
        """Test get_xpub_key_from_wallet function"""
        from helpers.hotwallethelpers import get_xpub_key_from_wallet

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1', 'word2', 'word3'],
            'passphrase': 'test_pass'
        }
        mock_get_xpub.return_value = 'xpub_key_result'

        result = get_xpub_key_from_wallet(account=0)

        self.assertEqual(result, 'xpub_key_result')
        mock_get_xpub.assert_called_once_with(
            mnemonic='word1 word2 word3',
            passphrase='test_pass',
            account=0
        )


class TestGetXprivKeyFromWallet(unittest.TestCase):
    """Test cases for get_xpriv_key_from_wallet function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpriv_key')
    def test_get_xpriv_key_from_wallet(self, mock_get_xpriv, mock_hot_wallet):
        """Test get_xpriv_key_from_wallet function"""
        from helpers.hotwallethelpers import get_xpriv_key_from_wallet

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1', 'word2'],
            'passphrase': 'pass'
        }
        mock_get_xpriv.return_value = 'xpriv_key_result'

        result = get_xpriv_key_from_wallet(account=1)

        self.assertEqual(result, 'xpriv_key_result')
        mock_get_xpriv.assert_called_once_with(
            mnemonic='word1 word2',
            passphrase='pass',
            account=1
        )


class TestGetPrivateKeyFromWallet(unittest.TestCase):
    """Test cases for get_private_key_from_wallet function"""

    @patch('helpers.hotwallethelpers.get_xpriv_key_from_wallet')
    @patch('helpers.hotwallethelpers.get_private_key')
    def test_get_private_key_from_wallet(self, mock_get_priv, mock_get_xpriv):
        """Test get_private_key_from_wallet function"""
        from helpers.hotwallethelpers import get_private_key_from_wallet

        mock_get_xpriv.return_value = 'xpriv_key'
        mock_get_priv.return_value = {'address': 'private_key'}

        result = get_private_key_from_wallet(account=0, index=5)

        self.assertEqual(result, {'address': 'private_key'})
        mock_get_xpriv.assert_called_once_with(account=0)
        mock_get_priv.assert_called_once_with(xpriv='xpriv_key', i=5)


class TestGetSingleAddressPrivateKey(unittest.TestCase):
    """Test cases for get_single_address_private_key function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    def test_get_single_address_private_key_found(self, mock_hot_wallet):
        """Test get_single_address_private_key when address is found"""
        from helpers.hotwallethelpers import get_single_address_private_key

        mock_hot_wallet.return_value = {
            '1Address1': 'private_key_1',
            '1Address2': 'private_key_2',
            'mnemonic': ['word1'],
            'passphrase': ''
        }

        result = get_single_address_private_key('1Address1')

        self.assertEqual(result, {'1Address1': 'private_key_1'})

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    def test_get_single_address_private_key_not_found(self, mock_hot_wallet):
        """Test get_single_address_private_key when address is not found"""
        from helpers.hotwallethelpers import get_single_address_private_key

        mock_hot_wallet.return_value = {
            '1Address1': 'private_key_1',
            'mnemonic': ['word1'],
            'passphrase': ''
        }

        result = get_single_address_private_key('1NonexistentAddress')

        self.assertIsNone(result)


class TestFindAddressInWallet(unittest.TestCase):
    """Test cases for find_address_in_wallet function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpub_key')
    @patch('helpers.hotwallethelpers.get_addresses_from_xpub')
    def test_find_address_in_wallet_found(self, mock_get_addrs, mock_get_xpub, mock_hot_wallet):
        """Test find_address_in_wallet when address is found"""
        from helpers.hotwallethelpers import find_address_in_wallet

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1', 'word2'],
            'passphrase': 'pass'
        }
        mock_get_xpub.return_value = 'xpub_key'
        mock_get_addrs.return_value = ['addr0', 'addr1', 'addr2', 'target_addr', 'addr4']

        account, index = find_address_in_wallet('target_addr', accounts=1, indexes=5)

        self.assertEqual(account, 0)
        self.assertEqual(index, 3)

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpub_key')
    @patch('helpers.hotwallethelpers.get_addresses_from_xpub')
    def test_find_address_in_wallet_not_found(self, mock_get_addrs, mock_get_xpub, mock_hot_wallet):
        """Test find_address_in_wallet when address is not found"""
        from helpers.hotwallethelpers import find_address_in_wallet

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1'],
            'passphrase': ''
        }
        mock_get_xpub.return_value = 'xpub_key'
        mock_get_addrs.return_value = ['addr0', 'addr1', 'addr2']

        account, index = find_address_in_wallet('nonexistent_addr', accounts=1, indexes=3)

        self.assertIsNone(account)
        self.assertIsNone(index)


class TestFindSingleAddressInWallet(unittest.TestCase):
    """Test cases for find_single_address_in_wallet function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    def test_find_single_address_in_wallet_found(self, mock_hot_wallet):
        """Test find_single_address_in_wallet when address is found"""
        from helpers.hotwallethelpers import find_single_address_in_wallet

        mock_hot_wallet.return_value = {
            '1Address1': 'private_key_1',
            'mnemonic': ['word1'],
            'passphrase': ''
        }

        result = find_single_address_in_wallet('1Address1')

        self.assertEqual(result, 'private_key_1')

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    def test_find_single_address_in_wallet_not_found(self, mock_hot_wallet):
        """Test find_single_address_in_wallet when address is not found"""
        from helpers.hotwallethelpers import find_single_address_in_wallet

        mock_hot_wallet.return_value = {
            '1Address1': 'private_key_1',
            'mnemonic': ['word1'],
            'passphrase': ''
        }

        result = find_single_address_in_wallet('1NonexistentAddress')

        self.assertIsNone(result)


class TestHotWalletSeed(unittest.TestCase):
    """Test cases for hot_wallet_seed function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_seed')
    def test_hot_wallet_seed(self, mock_get_seed, mock_hot_wallet):
        """Test hot_wallet_seed function"""
        from helpers.hotwallethelpers import hot_wallet_seed

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1', 'word2', 'word3'],
            'passphrase': 'test_pass'
        }
        mock_get_seed.return_value = b'seed_bytes'

        result = hot_wallet_seed()

        self.assertEqual(result, b'seed_bytes')
        mock_get_seed.assert_called_once_with(
            mnemonic='word1 word2 word3',
            passphrase='test_pass'
        )


class TestFindAccountByXpub(unittest.TestCase):
    """Test cases for find_account_by_xpub function"""

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpub_key')
    def test_find_account_by_xpub_found(self, mock_get_xpub, mock_hot_wallet):
        """Test find_account_by_xpub when xpub is found"""
        from helpers.hotwallethelpers import find_account_by_xpub

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1', 'word2'],
            'passphrase': 'pass'
        }
        # Return different xpubs for different accounts
        mock_get_xpub.side_effect = ['xpub0', 'xpub1', 'target_xpub', 'xpub3']

        result = find_account_by_xpub('target_xpub', n=5)

        self.assertEqual(result, 2)

    @patch('helpers.hotwallethelpers.get_hot_wallet')
    @patch('helpers.hotwallethelpers.get_xpub_key')
    def test_find_account_by_xpub_not_found(self, mock_get_xpub, mock_hot_wallet):
        """Test find_account_by_xpub when xpub is not found"""
        from helpers.hotwallethelpers import find_account_by_xpub

        mock_hot_wallet.return_value = {
            'mnemonic': ['word1'],
            'passphrase': ''
        }
        mock_get_xpub.side_effect = ['xpub0', 'xpub1', 'xpub2']

        result = find_account_by_xpub('nonexistent_xpub', n=3)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
