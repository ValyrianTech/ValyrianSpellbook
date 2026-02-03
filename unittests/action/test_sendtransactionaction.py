#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import mock

from action.sendtransactionaction import SendTransactionAction
from action.actiontype import ActionType
from action.transactiontype import TransactionType


class TestSendTransactionAction(object):
    """Tests for SendTransactionAction"""

    def test_sendtransactionaction_init(self):
        action = SendTransactionAction('test_send_tx')
        assert action.id == 'test_send_tx'
        assert action.action_type == ActionType.SENDTRANSACTION
        assert action.fee_address is None
        assert action.fee_percentage == 0
        assert action.fee_minimum_amount == 1000
        assert action.tx_fee_type == 'High'
        assert action.tx_fee == 0
        assert action.wallet_type is None
        assert action.sending_address is None
        assert action.receiving_address is None
        assert action.amount == 0
        assert action.transaction_type == TransactionType.SEND2SINGLE
        assert action.utxo_confirmations == 1
        assert action.private_key is None
        assert action.txid is None

    @mock.patch('action.sendtransactionaction.valid_address')
    def test_sendtransactionaction_configure_fee_address(self, mock_valid_address):
        mock_valid_address.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(fee_address='1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y')
        assert action.fee_address == '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'

    @mock.patch('action.sendtransactionaction.valid_percentage')
    def test_sendtransactionaction_configure_fee_percentage(self, mock_valid_percentage):
        mock_valid_percentage.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(fee_percentage=5)
        assert action.fee_percentage == 5

    def test_sendtransactionaction_configure_wallet_type_single(self):
        action = SendTransactionAction('test_send_tx')
        action.configure(wallet_type='Single')
        assert action.wallet_type == 'Single'

    @mock.patch('action.sendtransactionaction.get_address_from_wallet')
    def test_sendtransactionaction_configure_wallet_type_bip44(self, mock_get_address):
        mock_get_address.return_value = '1BIP44Address'
        action = SendTransactionAction('test_send_tx')
        action.configure(wallet_type='BIP44', bip44_account=0, bip44_index=0)
        assert action.wallet_type == 'BIP44'

    def test_sendtransactionaction_configure_wallet_type_invalid(self):
        action = SendTransactionAction('test_send_tx')
        action.configure(wallet_type='Invalid')
        assert action.wallet_type is None

    @mock.patch('action.sendtransactionaction.valid_address')
    def test_sendtransactionaction_configure_sending_address(self, mock_valid_address):
        mock_valid_address.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(sending_address='1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y')
        assert action.sending_address == '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'

    def test_sendtransactionaction_configure_bip44(self):
        action = SendTransactionAction('test_send_tx')
        action.configure(bip44_account=0, bip44_index=5)
        assert action.bip44_account == 0
        assert action.bip44_index == 5

    @mock.patch('action.sendtransactionaction.valid_address')
    def test_sendtransactionaction_configure_receiving_address(self, mock_valid_address):
        mock_valid_address.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(receiving_address='1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y')
        assert action.receiving_address == '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'

    @mock.patch('action.sendtransactionaction.valid_xpub')
    def test_sendtransactionaction_configure_receiving_xpub(self, mock_valid_xpub):
        mock_valid_xpub.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(receiving_xpub='xpub123')
        assert action.receiving_xpub == 'xpub123'

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_configure_amount(self, mock_valid_amount):
        mock_valid_amount.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(amount=50000)
        assert action.amount == 50000

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_configure_minimum_amount(self, mock_valid_amount):
        mock_valid_amount.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(minimum_amount=10000)
        assert action.minimum_amount == 10000

    @mock.patch('action.sendtransactionaction.valid_op_return')
    def test_sendtransactionaction_configure_op_return(self, mock_valid_op_return):
        mock_valid_op_return.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(op_return_data='test data')
        assert action.op_return_data == 'test data'

    @mock.patch('action.sendtransactionaction.valid_transaction_type')
    def test_sendtransactionaction_configure_transaction_type(self, mock_valid_tx_type):
        mock_valid_tx_type.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(transaction_type='Send2Many')
        assert action.transaction_type == 'Send2Many'

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_configure_minimum_output_value(self, mock_valid_amount):
        mock_valid_amount.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(minimum_output_value=546)
        assert action.minimum_output_value == 546

    @mock.patch('action.sendtransactionaction.valid_address')
    def test_sendtransactionaction_configure_registration_address(self, mock_valid_address):
        mock_valid_address.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(registration_address='1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y')
        assert action.registration_address == '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'

    @mock.patch('action.sendtransactionaction.valid_block_height')
    def test_sendtransactionaction_configure_registration_block_height(self, mock_valid_block_height):
        mock_valid_block_height.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(registration_block_height=700000)
        assert action.registration_block_height == 700000

    @mock.patch('action.sendtransactionaction.valid_xpub')
    def test_sendtransactionaction_configure_registration_xpub(self, mock_valid_xpub):
        mock_valid_xpub.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(registration_xpub='xpub456')
        assert action.registration_xpub == 'xpub456'

    @mock.patch('action.sendtransactionaction.valid_distribution')
    def test_sendtransactionaction_configure_distribution(self, mock_valid_distribution):
        mock_valid_distribution.return_value = True
        action = SendTransactionAction('test_send_tx')
        distribution = {'addr1': 50, 'addr2': 50}
        action.configure(distribution=distribution)
        assert action.distribution == distribution

    def test_sendtransactionaction_configure_tx_fee_type(self):
        for fee_type in ['High', 'Medium', 'Low', 'Fixed']:
            action = SendTransactionAction('test_send_tx')
            action.configure(tx_fee_type=fee_type)
            assert action.tx_fee_type == fee_type

        action_invalid = SendTransactionAction('test_send_tx')
        action_invalid.configure(tx_fee_type='Invalid')
        assert action_invalid.tx_fee_type == 'High'  # default

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_configure_tx_fee_fixed(self, mock_valid_amount):
        mock_valid_amount.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(tx_fee_type='Fixed', tx_fee=100)
        assert action.tx_fee == 100

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_configure_utxo_confirmations(self, mock_valid_amount):
        mock_valid_amount.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(utxo_confirmations=6)
        assert action.utxo_confirmations == 6

    @mock.patch('action.sendtransactionaction.valid_private_key')
    def test_sendtransactionaction_configure_private_key(self, mock_valid_private_key):
        mock_valid_private_key.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.configure(private_key='L1234567890abcdef')
        assert action.private_key == 'L1234567890abcdef'

    @mock.patch('action.sendtransactionaction.get_address_from_wallet')
    def test_sendtransactionaction_configure_bip44_wallet(self, mock_get_address):
        mock_get_address.return_value = '1BIP44Address'
        action = SendTransactionAction('test_send_tx')
        action.configure(wallet_type='BIP44', bip44_account=0, bip44_index=0)
        assert action.wallet_type == 'BIP44'
        assert action.sending_address == '1BIP44Address'
        mock_get_address.assert_called_once_with(0, 0)

    def test_sendtransactionaction_json_encodable(self):
        action = SendTransactionAction('test_send_tx')
        action.configure(created=1609459200)
        action.fee_address = 'fee_addr'
        action.fee_percentage = 5
        action.wallet_type = 'Single'
        action.sending_address = 'send_addr'
        action.receiving_address = 'recv_addr'
        action.amount = 50000
        action.transaction_type = 'Send2Single'
        
        result = action.json_encodable()
        assert result['id'] == 'test_send_tx'
        assert result['action_type'] == ActionType.SENDTRANSACTION
        assert result['fee_address'] == 'fee_addr'
        assert result['fee_percentage'] == 5
        assert result['wallet_type'] == 'Single'
        assert result['sending_address'] == 'send_addr'
        assert result['receiving_address'] == 'recv_addr'
        assert result['amount'] == 50000
        assert result['transaction_type'] == 'Send2Single'

    def test_sendtransactionaction_run_no_sending_address(self):
        action = SendTransactionAction('test_send_tx')
        result = action.run()
        assert result == False

    def test_sendtransactionaction_calculate_spellbook_fee_no_fee(self):
        action = SendTransactionAction('test_send_tx')
        action.fee_percentage = 0
        action.fee_address = None
        fee = action.calculate_spellbook_fee(100000)
        assert fee == 0

    def test_sendtransactionaction_calculate_spellbook_fee_with_percentage(self):
        action = SendTransactionAction('test_send_tx')
        action.fee_percentage = 5
        action.fee_address = '1FeeAddress'
        action.amount = 0  # sending all
        fee = action.calculate_spellbook_fee(100000)
        assert fee == 5000  # 5% of 100000

    def test_sendtransactionaction_calculate_spellbook_fee_minimum(self):
        action = SendTransactionAction('test_send_tx')
        action.fee_percentage = 1
        action.fee_address = '1FeeAddress'
        action.fee_minimum_amount = 2000
        action.amount = 0
        fee = action.calculate_spellbook_fee(10000)  # 1% = 100, but minimum is 2000
        assert fee == 2000

    def test_sendtransactionaction_calculate_spellbook_fee_specific_amount(self):
        action = SendTransactionAction('test_send_tx')
        action.fee_percentage = 10
        action.fee_address = '1FeeAddress'
        action.amount = 50000  # specific amount
        fee = action.calculate_spellbook_fee(100000)
        assert fee == 5000  # 10% of 50000 (amount), not 100000 (total)

    def test_sendtransactionaction_construct_transaction_outputs_empty(self):
        outputs = SendTransactionAction.construct_transaction_outputs()
        assert outputs == []

    def test_sendtransactionaction_is_fee_acceptable(self):
        action = SendTransactionAction('test_send_tx')
        # Default max fee percentage from config
        with mock.patch('action.sendtransactionaction.get_max_tx_fee_percentage', return_value=10):
            # 5% fee should be acceptable
            assert action.is_fee_acceptable(5000, 100000) == True
            # 15% fee should not be acceptable
            assert action.is_fee_acceptable(15000, 100000) == False

    def test_sendtransactionaction_log_transaction_info(self):
        action = SendTransactionAction('test_send_tx')
        # Just verify it doesn't raise an error
        tx_inputs = [{'address': '1Test', 'value': 50000, 'output': 'hash:0', 'confirmations': 6}]
        tx_outputs = [{'address': '1Recv', 'value': 49000}]
        action.log_transaction_info(tx_inputs=tx_inputs, tx_outputs=tx_outputs)

    @mock.patch('action.sendtransactionaction.valid_address')
    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_get_distribution_send2single(self, mock_valid_amount, mock_valid_address):
        mock_valid_amount.return_value = True
        mock_valid_address.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.receiving_address = '1RecvAddress'
        distribution = action.get_distribution('Send2Single', 50000)
        assert distribution == {'1RecvAddress': 50000}

    @mock.patch('action.sendtransactionaction.valid_amount')
    def test_sendtransactionaction_get_distribution_invalid_amount(self, mock_valid_amount):
        mock_valid_amount.return_value = False
        action = SendTransactionAction('test_send_tx')
        with pytest.raises(Exception) as exc_info:
            action.get_distribution('Send2Single', 0)
        assert 'invalid sending_amount' in str(exc_info.value)

    @mock.patch('action.sendtransactionaction.valid_amount')
    @mock.patch('action.sendtransactionaction.valid_address')
    def test_sendtransactionaction_get_distribution_send2single_invalid_address(self, mock_valid_address, mock_valid_amount):
        mock_valid_amount.return_value = True
        mock_valid_address.return_value = False
        action = SendTransactionAction('test_send_tx')
        action.receiving_address = 'invalid'
        with pytest.raises(Exception) as exc_info:
            action.get_distribution('Send2Single', 50000)
        assert 'invalid receiving_address' in str(exc_info.value)

    @mock.patch('action.sendtransactionaction.valid_amount')
    @mock.patch('action.sendtransactionaction.valid_distribution')
    def test_sendtransactionaction_get_distribution_send2many(self, mock_valid_distribution, mock_valid_amount):
        mock_valid_amount.return_value = True
        mock_valid_distribution.return_value = True
        action = SendTransactionAction('test_send_tx')
        action.distribution = {'addr1': 50, 'addr2': 50}
        distribution = action.get_distribution('Send2Many', 50000)
        assert distribution == {'addr1': 50, 'addr2': 50}

    @mock.patch('action.sendtransactionaction.valid_amount')
    @mock.patch('action.sendtransactionaction.valid_distribution')
    def test_sendtransactionaction_get_distribution_send2many_invalid(self, mock_valid_distribution, mock_valid_amount):
        mock_valid_amount.return_value = True
        mock_valid_distribution.return_value = False
        action = SendTransactionAction('test_send_tx')
        action.distribution = None
        with pytest.raises(Exception) as exc_info:
            action.get_distribution('Send2Many', 50000)
        assert 'invalid distribution' in str(exc_info.value)

    @mock.patch('action.sendtransactionaction.get_hot_wallet')
    def test_sendtransactionaction_get_private_key_single(self, mock_get_hot_wallet):
        mock_get_hot_wallet.return_value = {'1SendAddress': 'private_key_123'}
        action = SendTransactionAction('test_send_tx')
        action.wallet_type = 'Single'
        action.sending_address = '1SendAddress'
        keys = action.get_private_key()
        assert keys == {'1SendAddress': 'private_key_123'}

    @mock.patch('action.sendtransactionaction.get_hot_wallet')
    def test_sendtransactionaction_get_private_key_single_not_found(self, mock_get_hot_wallet):
        mock_get_hot_wallet.return_value = {'1OtherAddress': 'other_key'}
        action = SendTransactionAction('test_send_tx')
        action.wallet_type = 'Single'
        action.sending_address = '1SendAddress'
        keys = action.get_private_key()
        assert keys == {}

    @mock.patch('action.sendtransactionaction.get_private_key')
    @mock.patch('action.sendtransactionaction.get_xpriv_key')
    @mock.patch('action.sendtransactionaction.get_hot_wallet')
    def test_sendtransactionaction_get_private_key_bip44(self, mock_get_hot_wallet, mock_get_xpriv, mock_get_priv):
        mock_get_hot_wallet.return_value = {'mnemonic': ['word1', 'word2'], 'passphrase': 'pass'}
        mock_get_xpriv.return_value = 'xpriv_key'
        mock_get_priv.return_value = {'1BIP44Address': 'bip44_private_key'}
        
        action = SendTransactionAction('test_send_tx')
        action.wallet_type = 'BIP44'
        action.bip44_account = 0
        action.bip44_index = 0
        keys = action.get_private_key()
        
        assert keys == {'1BIP44Address': 'bip44_private_key'}
        mock_get_xpriv.assert_called_once_with(mnemonic='word1 word2', passphrase='pass', account=0)
        mock_get_priv.assert_called_once_with('xpriv_key', 0)

    @mock.patch('action.sendtransactionaction.get_hot_wallet')
    def test_sendtransactionaction_get_private_key_unknown_wallet_type(self, mock_get_hot_wallet):
        mock_get_hot_wallet.return_value = {}
        action = SendTransactionAction('test_send_tx')
        action.wallet_type = 'Unknown'
        with pytest.raises(NotImplementedError) as exc_info:
            action.get_private_key()
        assert 'Unknown wallet type' in str(exc_info.value)
