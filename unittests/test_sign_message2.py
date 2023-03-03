#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from bips.BIP32 import set_chain_mode
from helpers.hotwallethelpers import get_address_from_wallet, get_private_key_from_wallet
from helpers.messagehelpers import verify_message, sign_message
from helpers.configurationhelpers import get_use_testnet


class TestSignMessage(object):
    # For some reason there are multiple possible valid signatures, testing both the signatures found on the
    # https://github.com/stequald/bitcoin-sign-message readme as the ones that are actually calculated

    def test_sign_message_with_compressed_address(self):
        address = '14dD6ygPi5WXdwwBTt1FBZK3aD8uDem1FY'
        private_key = 'L41XHGJA5QX43QRG3FEwPbqD5BYvy6WxUxqAMM9oQdHJ5FcRHcGk'
        message = 'test message'

        print('Address:', address)
        print('Message:', message)

        # signature keeps changing, sign_input_message both signs and verifies
        signature = sign_message(message, private_key)
        print('Signature:', signature)

        assert verify_message(address=address, message=message, signature=signature)
