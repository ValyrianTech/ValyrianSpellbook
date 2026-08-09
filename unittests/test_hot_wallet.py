#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for hot_wallet.py — the hot wallet management CLI.

hot_wallet.py reads configuration and runs argparse at module level, so we
patch sys.argv before importing to prevent it from consuming pytest arguments.
"""
import argparse
import importlib.util
import os
import sys

import mock
import pytest

# hot_wallet.py runs argparse and command dispatch at module level.
# Load the file directly via importlib to avoid package shadowing.
_HOT_WALLET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hot_wallet.py')

if 'hot_wallet' in sys.modules:
    del sys.modules['hot_wallet']

with mock.patch('sys.argv', ['hot_wallet.py']):
    _spec = importlib.util.spec_from_file_location('hot_wallet', _HOT_WALLET_PATH)
    assert _spec is not None
    assert _spec.loader is not None
    hot_wallet = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(hot_wallet)
    sys.modules['hot_wallet'] = hot_wallet


def make_args(**kwargs):
    """Create an argparse.Namespace with the given attributes."""
    return argparse.Namespace(**kwargs)


class TestLoadWallet(object):

    @mock.patch('hot_wallet.os.path.isfile', return_value=False)
    def test_no_wallet_file_returns_empty(self, mock_isfile):
        hot_wallet.args = make_args(wallet=None, wallet_password=None)
        result = hot_wallet.load_wallet()
        assert result == {}

    @mock.patch('hot_wallet.simplejson.loads', return_value={'addr1': 'key1'})
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='encrypted_data')
    @mock.patch('hot_wallet.os.path.isfile', return_value=True)
    def test_load_with_password(self, mock_isfile, mock_open, mock_aes, mock_loads):
        hot_wallet.args = make_args(wallet=None, wallet_password='mypassword')
        mock_cipher = mock_aes.return_value
        mock_cipher.decrypt.return_value = 'decrypted_json'
        result = hot_wallet.load_wallet()
        assert result == {'addr1': 'key1'}
        mock_aes.assert_called_once_with(key='mypassword')
        mock_cipher.decrypt.assert_called_once_with('encrypted_data')

    @mock.patch('hot_wallet.getpass.getpass', return_value='interactive_pass')
    @mock.patch('hot_wallet.simplejson.loads', return_value={'addr': 'k'})
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='enc')
    @mock.patch('hot_wallet.os.path.isfile', return_value=True)
    def test_load_interactive_password(self, mock_isfile, mock_open, mock_aes, mock_loads, mock_getpass):
        hot_wallet.args = make_args(wallet=None, wallet_password=None)
        mock_cipher = mock_aes.return_value
        mock_cipher.decrypt.return_value = 'decrypted'
        result = hot_wallet.load_wallet()
        assert result == {'addr': 'k'}
        mock_getpass.assert_called_once()
        mock_aes.assert_called_once_with(key='interactive_pass')

    @mock.patch('hot_wallet.simplejson.loads', return_value={'a': 'b'})
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='enc')
    @mock.patch('hot_wallet.os.path.isfile', return_value=True)
    def test_load_with_wallet_arg(self, mock_isfile, mock_open, mock_aes, mock_loads):
        hot_wallet.args = make_args(wallet='custom_wallet', wallet_password='pass')
        mock_cipher = mock_aes.return_value
        mock_cipher.decrypt.return_value = 'decrypted'
        hot_wallet.load_wallet()
        assert hot_wallet.WALLET_ID == 'custom_wallet'

    @mock.patch('hot_wallet.sys.exit')
    @mock.patch('builtins.print')
    @mock.patch('builtins.open', side_effect=IOError('File not found'))
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('hot_wallet.os.path.isfile', return_value=True)
    def test_load_io_error(self, mock_isfile, mock_aes, mock_open, mock_print, mock_exit):
        hot_wallet.args = make_args(wallet=None, wallet_password='pass')
        mock_cipher = mock_aes.return_value
        mock_cipher.decrypt.return_value = 'decrypted'
        hot_wallet.load_wallet()
        mock_exit.assert_called_once_with(1)

    @mock.patch('hot_wallet.sys.exit')
    @mock.patch('builtins.print')
    @mock.patch('hot_wallet.simplejson.loads', side_effect=Exception('Bad decrypt'))
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('builtins.open', new_callable=mock.mock_open, read_data='enc')
    @mock.patch('hot_wallet.os.path.isfile', return_value=True)
    def test_load_decrypt_error(self, mock_isfile, mock_open, mock_aes, mock_loads, mock_print, mock_exit):
        hot_wallet.args = make_args(wallet=None, wallet_password='pass')
        mock_cipher = mock_aes.return_value
        mock_cipher.decrypt.return_value = 'decrypted'
        hot_wallet.load_wallet()
        mock_exit.assert_called_once_with(1)


class TestSaveWallet(object):

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('hot_wallet.simplejson.dumps', return_value='{"addr": "key"}')
    def test_save_with_password(self, mock_dumps, mock_aes, mock_open):
        hot_wallet.args = make_args(wallet_password='mypassword')
        mock_cipher = mock_aes.return_value
        mock_cipher.encrypt.return_value = b'encrypted_data'
        hot_wallet.save_wallet({'addr': 'key'})
        mock_aes.assert_called_once_with(key='mypassword')
        mock_cipher.encrypt.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('hot_wallet.simplejson.dumps', return_value='{"addr": "key"}')
    @mock.patch('hot_wallet.getpass.getpass', side_effect=['pass1', 'pass1'])
    def test_save_interactive_password_match(self, mock_getpass, mock_dumps, mock_aes, mock_open):
        hot_wallet.args = make_args(wallet_password=None)
        mock_aes.return_value.encrypt.return_value = b'encrypted'
        hot_wallet.save_wallet({'addr': 'key'})
        assert mock_getpass.call_count == 2
        mock_aes.assert_called_once_with(key='pass1')
        mock_aes.return_value.encrypt.assert_called_once()

    @mock.patch('hot_wallet.sys.exit')
    @mock.patch('builtins.print')
    @mock.patch('hot_wallet.getpass.getpass', side_effect=['pass1', 'pass2'])
    def test_save_interactive_password_mismatch(self, mock_getpass, mock_print, mock_exit):
        hot_wallet.args = make_args(wallet_password=None)
        hot_wallet.save_wallet({'addr': 'key'})
        mock_exit.assert_called_once_with(1)

    @mock.patch('builtins.open', new_callable=mock.mock_open)
    @mock.patch('hot_wallet.AESCipher')
    @mock.patch('hot_wallet.simplejson.dumps', return_value='{}')
    def test_save_empty_password(self, mock_dumps, mock_aes, mock_open):
        hot_wallet.args = make_args(wallet_password='')
        mock_cipher = mock_aes.return_value
        mock_cipher.encrypt.return_value = b'enc'
        hot_wallet.save_wallet({})
        mock_aes.assert_called_once_with(key='')


class TestAddKey(object):

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.privkey_to_address', return_value='1TestAddress')
    @mock.patch('hot_wallet.get_use_testnet', return_value=False)
    @mock.patch('hot_wallet.load_wallet', return_value={'existing': 'key'})
    def test_add_key_valid(self, mock_load, mock_testnet, mock_privkey, mock_save):
        hot_wallet.args = make_args(private_key='5myprivatekey123', wallet=None, wallet_password='pass')
        hot_wallet.add_key()
        mock_privkey.assert_called_once_with('5myprivatekey123', magicbyte=0)
        mock_save.assert_called_once_with({'existing': 'key', '1TestAddress': '5myprivatekey123'})

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.privkey_to_address', return_value='1TestAddr')
    @mock.patch('hot_wallet.get_use_testnet', return_value=True)
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_add_key_testnet(self, mock_load, mock_testnet, mock_privkey, mock_save):
        hot_wallet.args = make_args(private_key='5myprivatekey123', wallet=None, wallet_password='pass')
        hot_wallet.add_key()
        mock_privkey.assert_called_once_with('5myprivatekey123', magicbyte=111)
        mock_save.assert_called_once_with({'1TestAddr': '5myprivatekey123'})

    @mock.patch('hot_wallet.sys.exit', side_effect=SystemExit(1))
    @mock.patch('builtins.print')
    @mock.patch('hot_wallet.privkey_to_address', side_effect=AssertionError('bad key'))
    @mock.patch('hot_wallet.get_use_testnet', return_value=False)
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_add_key_invalid(self, mock_load, mock_testnet, mock_privkey, mock_print, mock_exit):
        hot_wallet.args = make_args(private_key='invalid', wallet=None, wallet_password='pass')
        with pytest.raises(SystemExit):
            hot_wallet.add_key()
        mock_exit.assert_called_once_with(1)


class TestDeleteKey(object):

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={'addr1': 'key1', 'addr2': 'key2'})
    def test_delete_existing_key(self, mock_load, mock_save):
        hot_wallet.args = make_args(address='addr1', wallet=None, wallet_password='pass')
        hot_wallet.delete_key()
        mock_save.assert_called_once_with({'addr2': 'key2'})

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={'addr1': 'key1'})
    def test_delete_non_existing_key(self, mock_load, mock_save):
        hot_wallet.args = make_args(address='nonexistent', wallet=None, wallet_password='pass')
        hot_wallet.delete_key()
        mock_save.assert_called_once_with({'addr1': 'key1'})

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_delete_from_empty_wallet(self, mock_load, mock_save):
        hot_wallet.args = make_args(address='addr1', wallet=None, wallet_password='pass')
        hot_wallet.delete_key()
        mock_save.assert_called_once_with({})


class TestSetBip44(object):

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_set_bip44_12_words(self, mock_load, mock_save):
        words = ['word'] * 12
        hot_wallet.args = make_args(mnemonic=words, passphrase=None, wallet=None, wallet_password='pass')
        hot_wallet.set_bip44()
        mock_save.assert_called_once_with({'mnemonic': words, 'passphrase': ''})

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_set_bip44_24_words(self, mock_load, mock_save):
        words = ['word'] * 24
        hot_wallet.args = make_args(mnemonic=words, passphrase='secret', wallet=None, wallet_password='pass')
        hot_wallet.set_bip44()
        mock_save.assert_called_once_with({'mnemonic': words, 'passphrase': 'secret'})

    @mock.patch('hot_wallet.save_wallet')
    @mock.patch('hot_wallet.load_wallet', return_value={'existing': 'data'})
    def test_set_bip44_preserves_existing(self, mock_load, mock_save):
        words = ['word'] * 12
        hot_wallet.args = make_args(mnemonic=words, passphrase='pass', wallet=None, wallet_password='pass')
        hot_wallet.set_bip44()
        mock_save.assert_called_once_with({'existing': 'data', 'mnemonic': words, 'passphrase': 'pass'})

    @mock.patch('hot_wallet.sys.exit')
    @mock.patch('builtins.print')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_set_bip44_invalid_word_count(self, mock_load, mock_print, mock_exit):
        hot_wallet.args = make_args(mnemonic=['word'] * 15, passphrase=None, wallet=None, wallet_password='pass')
        hot_wallet.set_bip44()
        mock_exit.assert_called_once_with(1)

    @mock.patch('hot_wallet.sys.exit')
    @mock.patch('builtins.print')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_set_bip44_too_few_words(self, mock_load, mock_print, mock_exit):
        hot_wallet.args = make_args(mnemonic=['word'] * 6, passphrase=None, wallet=None, wallet_password='pass')
        hot_wallet.set_bip44()
        mock_exit.assert_called_once_with(1)


class TestShow(object):

    @mock.patch('hot_wallet.pprint')
    @mock.patch('hot_wallet.load_wallet', return_value={'addr1': 'key1'})
    def test_show(self, mock_load, mock_pprint):
        hot_wallet.args = make_args(wallet=None, wallet_password='pass')
        hot_wallet.show()
        mock_pprint.assert_called_once_with({'addr1': 'key1'})

    @mock.patch('hot_wallet.pprint')
    @mock.patch('hot_wallet.load_wallet', return_value={})
    def test_show_empty_wallet(self, mock_load, mock_pprint):
        hot_wallet.args = make_args(wallet=None, wallet_password='pass')
        hot_wallet.show()
        mock_pprint.assert_called_once_with({})


class TestModuleLevel(object):

    def test_no_command(self):
        """When imported with no subcommand, args.command is None and no function runs."""
        assert getattr(hot_wallet.args, 'command', None) is None

    def test_wallet_dir_configured(self):
        assert hot_wallet.WALLET_DIR is not None
        assert hot_wallet.WALLET_ID is not None

    def test_parser_has_subcommands(self):
        """Verify the parser was set up with all expected subcommands."""
        # add_key requires a private_key positional argument
        ns = hot_wallet.parser.parse_args(['add_key', 'mykey', '-w', 'testwallet'])
        assert ns.command == 'add_key'
        assert ns.private_key == 'mykey'

        # delete_key requires an address positional argument
        ns = hot_wallet.parser.parse_args(['delete_key', '1Addr', '-w', 'testwallet'])
        assert ns.command == 'delete_key'
        assert ns.address == '1Addr'

        # set_bip44 requires mnemonic words
        ns = hot_wallet.parser.parse_args(['set_bip44', 'word1', 'word2', '-w', 'testwallet'])
        assert ns.command == 'set_bip44'
        assert ns.mnemonic == ['word1', 'word2']

        # show has no positional arguments
        ns = hot_wallet.parser.parse_args(['show', '-w', 'testwallet'])
        assert ns.command == 'show'
