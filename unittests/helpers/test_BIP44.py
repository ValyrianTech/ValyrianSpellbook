#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestBIP44Wallet(unittest.TestCase):
    """Test cases for BIP44Wallet class"""

    @patch('helpers.BIP44.get_xpub_keys')
    @patch('helpers.BIP44.get_xpriv_keys')
    @patch('helpers.BIP44.get_addresses_from_xpub')
    @patch('helpers.BIP44.get_change_addresses_from_xpub')
    def test_wallet_init(self, mock_change_addr, mock_addr, mock_xpriv, mock_xpub):
        """Test BIP44Wallet initialization"""
        from helpers.BIP44 import BIP44Wallet
        
        mock_xpub.return_value = ['xpub_key_0']
        mock_xpriv.return_value = ['xpriv_key_0']
        mock_addr.return_value = ['addr1', 'addr2']
        mock_change_addr.return_value = ['change1', 'change2']
        
        wallet = BIP44Wallet(
            mnemonic='abandon ' * 11 + 'about',
            passphrase='test',
            account=0,
            n=2
        )
        
        self.assertEqual(wallet.mnemonic, 'abandon ' * 11 + 'about')
        self.assertEqual(wallet.passphrase, 'test')
        self.assertEqual(wallet.account, 0)
        self.assertEqual(wallet.n, 2)
        self.assertEqual(wallet.addresses, ['addr1', 'addr2'])
        self.assertEqual(wallet.change_addresses, ['change1', 'change2'])

    @patch('helpers.BIP44.get_xpub_keys')
    @patch('helpers.BIP44.get_xpriv_keys')
    @patch('helpers.BIP44.get_addresses_from_xpub')
    @patch('helpers.BIP44.get_change_addresses_from_xpub')
    def test_wallet_init_default_params(self, mock_change_addr, mock_addr, mock_xpriv, mock_xpub):
        """Test BIP44Wallet initialization with default parameters"""
        from helpers.BIP44 import BIP44Wallet
        
        mock_xpub.return_value = ['xpub_key_0']
        mock_xpriv.return_value = ['xpriv_key_0']
        mock_addr.return_value = ['addr1']
        mock_change_addr.return_value = ['change1']
        
        wallet = BIP44Wallet(mnemonic='test mnemonic')
        
        self.assertEqual(wallet.passphrase, '')
        self.assertEqual(wallet.account, 0)
        self.assertEqual(wallet.n, 100)

    @patch('helpers.BIP44.get_xpub_keys')
    @patch('helpers.BIP44.get_xpriv_keys')
    @patch('helpers.BIP44.get_addresses_from_xpub')
    @patch('helpers.BIP44.get_change_addresses_from_xpub')
    @patch('helpers.BIP44.requests.get')
    @patch('helpers.BIP44.time.sleep')
    @patch('helpers.BIP44.get_private_key')
    @patch('helpers.BIP44.pprint')
    def test_wallet_scan_no_balance(self, mock_pprint, mock_get_priv, mock_sleep, mock_requests, 
                                     mock_change_addr, mock_addr, mock_xpriv, mock_xpub):
        """Test BIP44Wallet scan with no balance"""
        from helpers.BIP44 import BIP44Wallet
        
        mock_xpub.return_value = ['xpub_key_0']
        mock_xpriv.return_value = ['xpriv_key_0']
        mock_addr.return_value = ['addr1', 'addr2']
        mock_change_addr.return_value = ['change1', 'change2']
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'addresses': [
                {'address': 'addr1', 'final_balance': 0},
                {'address': 'addr2', 'final_balance': 0}
            ]
        }
        mock_requests.return_value = mock_response
        
        wallet = BIP44Wallet(mnemonic='test', n=2)
        result = wallet.scan()
        
        self.assertEqual(result, {})

    @patch('helpers.BIP44.get_xpub_keys')
    @patch('helpers.BIP44.get_xpriv_keys')
    @patch('helpers.BIP44.get_addresses_from_xpub')
    @patch('helpers.BIP44.get_change_addresses_from_xpub')
    def test_wallet_attributes(self, mock_change_addr, mock_addr, mock_xpriv, mock_xpub):
        """Test BIP44Wallet attributes after initialization"""
        from helpers.BIP44 import BIP44Wallet
        
        mock_xpub.return_value = ['xpub_key_0']
        mock_xpriv.return_value = ['xpriv_key_0']
        mock_addr.return_value = ['addr1', 'addr2']
        mock_change_addr.return_value = ['change1', 'change2']
        
        wallet = BIP44Wallet(mnemonic='test mnemonic', passphrase='pass', n=2)
        
        self.assertEqual(wallet.xpub_keys, ['xpub_key_0'])
        self.assertEqual(wallet.xpriv_keys, ['xpriv_key_0'])
        self.assertEqual(len(wallet.addresses), 2)
        self.assertEqual(len(wallet.change_addresses), 2)

    @patch('helpers.BIP44.get_xpub_keys')
    @patch('helpers.BIP44.get_xpriv_keys')
    @patch('helpers.BIP44.get_addresses_from_xpub')
    @patch('helpers.BIP44.get_change_addresses_from_xpub')
    def test_wallet_sweep_not_implemented(self, mock_change_addr, mock_addr, mock_xpriv, mock_xpub):
        """Test BIP44Wallet sweep method (not implemented)"""
        from helpers.BIP44 import BIP44Wallet
        
        mock_xpub.return_value = ['xpub_key_0']
        mock_xpriv.return_value = ['xpriv_key_0']
        mock_addr.return_value = ['addr1']
        mock_change_addr.return_value = ['change1']
        
        wallet = BIP44Wallet(mnemonic='test', n=1)
        result = wallet.sweep('destination_address')
        
        self.assertIsNone(result)


class TestSetTestnet(unittest.TestCase):
    """Test cases for set_testnet function"""

    def setUp(self):
        """Reset to mainnet before each test"""
        from helpers.BIP44 import set_testnet
        set_testnet(False)

    def tearDown(self):
        """Reset to mainnet after each test"""
        from helpers.BIP44 import set_testnet
        set_testnet(False)

    def test_set_testnet_true(self):
        """Test setting testnet mode"""
        from helpers.BIP44 import set_testnet
        from bips.BIP32 import TESTNET_PRIVATE
        
        set_testnet(True)
        
        # Import again to get updated values
        import helpers.BIP44 as bip44_module
        self.assertEqual(bip44_module.MAGICBYTE, 111)
        self.assertEqual(bip44_module.VBYTES, TESTNET_PRIVATE)
        self.assertEqual(bip44_module.COIN_TYPE, 1)

    def test_set_testnet_false(self):
        """Test setting mainnet mode"""
        from helpers.BIP44 import set_testnet
        from bips.BIP32 import MAINNET_PRIVATE
        
        set_testnet(False)
        
        import helpers.BIP44 as bip44_module
        self.assertEqual(bip44_module.MAGICBYTE, 0)
        self.assertEqual(bip44_module.VBYTES, MAINNET_PRIVATE)
        self.assertEqual(bip44_module.COIN_TYPE, 0)


class TestShowDetails(unittest.TestCase):
    """Test cases for show_details function"""

    @patch('helpers.BIP44.get_seed')
    @patch('helpers.BIP44.bip32_master_key')
    @patch('helpers.BIP44.bip32_extract_key')
    @patch('helpers.BIP44.encode_privkey')
    @patch('helpers.BIP44.bip32_privtopub')
    @patch('helpers.BIP44.pubkey_to_address')
    @patch('helpers.BIP44.bip32_ckd')
    @patch('helpers.BIP44.privkey_to_pubkey')
    @patch('builtins.print')
    def test_show_details(self, mock_print, mock_priv_to_pub, mock_ckd, mock_pub_to_addr,
                          mock_privtopub, mock_encode, mock_extract, mock_master, mock_seed):
        """Test show_details function"""
        from helpers.BIP44 import show_details
        
        mock_seed.return_value = b'test_seed_bytes_here_1234567890'
        mock_master.return_value = 'master_key'
        mock_extract.return_value = 'extracted_key'
        mock_encode.return_value = 'encoded_key'
        mock_privtopub.return_value = 'public_key'
        mock_pub_to_addr.return_value = 'address'
        mock_ckd.return_value = 'derived_key'
        mock_priv_to_pub.return_value = 'pubkey_hex'
        
        result = show_details('test mnemonic', passphrase='test', n_accounts=1)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    @patch('helpers.BIP44.get_seed')
    @patch('helpers.BIP44.bip32_master_key')
    @patch('helpers.BIP44.bip32_extract_key')
    @patch('helpers.BIP44.encode_privkey')
    @patch('helpers.BIP44.bip32_privtopub')
    @patch('helpers.BIP44.pubkey_to_address')
    @patch('helpers.BIP44.bip32_ckd')
    @patch('helpers.BIP44.privkey_to_pubkey')
    @patch('builtins.print')
    def test_show_details_multiple_accounts(self, mock_print, mock_priv_to_pub, mock_ckd, 
                                             mock_pub_to_addr, mock_privtopub, mock_encode, 
                                             mock_extract, mock_master, mock_seed):
        """Test show_details with multiple accounts"""
        from helpers.BIP44 import show_details
        
        mock_seed.return_value = b'test_seed_bytes_here_1234567890'
        mock_master.return_value = 'master_key'
        mock_extract.return_value = 'extracted_key'
        mock_encode.return_value = 'encoded_key'
        mock_privtopub.return_value = 'public_key'
        mock_pub_to_addr.return_value = 'address'
        mock_ckd.return_value = 'derived_key'
        mock_priv_to_pub.return_value = 'pubkey_hex'
        
        result = show_details('test mnemonic', n_accounts=3)
        
        self.assertEqual(len(result), 3)


class TestModuleConstants(unittest.TestCase):
    """Test module constants"""

    def test_hardened_constant(self):
        """Test HARDENED constant value"""
        from helpers.BIP44 import HARDENED
        self.assertEqual(HARDENED, 2**31)

    def test_default_magicbyte(self):
        """Test default MAGICBYTE for mainnet"""
        from helpers.BIP44 import set_testnet
        set_testnet(False)
        import helpers.BIP44 as bip44_module
        self.assertEqual(bip44_module.MAGICBYTE, 0)


if __name__ == '__main__':
    unittest.main()
