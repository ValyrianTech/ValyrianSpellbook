#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pytest
import mock
from validators import validators
import helpers.configurationhelpers


# Change working dir up one level
os.chdir("..")


class TestValidators(object):
    def test_pytest(self):
        print 'testing pytest...',
        assert True

    @pytest.mark.parametrize('address, expected, description', [
        ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', True, "Normal valid address"],
        [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', True, "unicode valid address"],
        ['1SansacmMr38bdzGkzruDVajEsZuiZHx9', True, "Normal valid address"],
        ['1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8', True, "Normal valid address"],
        ['3AL6xh1qn4m83ni9vfTh6WarHBn1Ew1CZk', True, "Multisig valid address"],
        ['4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, starts with 4"],
        ['1Rlbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains l"],
        ['1RObbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains O"],
        ['1RIbbk6PuJst6ot6ay2DcVugv8nxfJh5y', False, "invalid address, contains I"],
        ['123456789a123456789a12345', False, "address shorter than 26 characters"],
        ['123456789a123456789a123456789a123456', False, "address longer than 35 characters"],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_address_mainnet(self, address, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=False)
        print description
        assert validators.valid_address(address) == expected, description

    @pytest.mark.parametrize('address, expected, description', [
        ['miwEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', True, "Normal valid address"],
        [u'miwEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', True, "unicode valid address"],
        ['2NA61aPdv3JAVcqwJSHvUcygkJeWaWsMKJ8', True, "Multisig valid address"],
        ['1iwEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', False, "invalid address, starts with 1"],
        ['mlwEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', False, "invalid address, contains l"],
        ['m0wEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', False, "invalid address, contains O"],
        ['mIwEV9pnnQtetsETmdVLzLmrw3jcT3QKdb', False, "invalid address, contains I"],
        ['m23456789a123456789a12345', False, "address shorter than 26 characters"],
        ['m23456789a123456789a123456789a123456', False, "address longer than 35 characters"],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_address_testnet(self, address, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=True)
        print description
        assert validators.valid_address(address) == expected, description

    @pytest.mark.parametrize('xpub, expected, description', [
        ['xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', True, 'valid xpub'],
        ['6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', False, 'no xpub at beginning'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_xpub_mainnet(self, xpub, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=False)
        print description
        assert validators.valid_xpub(xpub) == expected, description

    @pytest.mark.parametrize('xpub, expected, description', [
        ['tpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', True, 'valid xpub'],
        ['6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD', False, 'no xpub at beginning'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_xpub_testnet(self, xpub, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=True)
        print description
        assert validators.valid_xpub(xpub) == expected, description

    @pytest.mark.parametrize('txid, expected, description', [
        ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', True, 'valid txid'],
        ['Bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', False, 'capital B'],
        ['gdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b7', False, 'letter g'],
        ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b', False, '63 characters'],
        ['bdd523f0171814cc1dcd28cb851ba9e68eb8f26eca03e4d3b0d0c6ca7d20d0b77', False, '64 characters'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_txid(self, txid, expected, description):
        print description
        assert validators.valid_txid(txid) == expected

    @pytest.mark.parametrize('text, expected, description', [
        ['this is a valid description', True, 'valid description'],
        ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False, 'too long'],
        ['', True, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_description(self, text, expected, description):
        print description
        assert validators.valid_description(text) == expected

    @pytest.mark.parametrize('message, expected, description', [
        ['test', True, 'valid op_return'],
        ['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', False, 'invalid op_return: 81 characters'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_op_return(self, message, expected, description):
        print description
        assert validators.valid_op_return(message) == expected

    @pytest.mark.parametrize('message, expected, description', [
        ['@0:NAME=Robb Stark', True, 'valid message'],
        ['@0:NAME=Sansa Stark', True, 'valid message'],
        ['@0:HOUSE=Stark|@1:HOUSE=Stark', True, 'valid message'],
        ['0@1:RELATION=Brother|1@0:RELATION=Sister', True, 'valid message'],
        ['this message has exactly 80 characters and should be accepted by the blockchain!', False, 'invalid message'],
        ['test', False, 'invalid message'],
        ['@0:HOUSEStark|@1:HOUSE=Stark', False, 'invalid first part'],
        ['@0:HOUSE=Stark|@1:HOUSEStark', False, 'invalid second part'],
        ['0:NAME=Robb Stark', False, 'no @ character'],
        ['@0NAME=Robb Stark', False, 'no : character'],
        ['@0:NAMERobb Stark', False, 'no = character'],
        ['d@0:NAME=Robb Stark', False, 'FROM is not an integer or empty'],
        ['@d:NAME=Robb Stark', False, 'TO is not an integer'],
        ['@0:N_AME=Robb Stark', False, '_ in variable name'],
        ['@0:N AME=Robb Stark', False, 'whitespace in variable name'],
        ['@0:NAME=Robb? Stark', False, '? character in value'],
        ['@0:NAME=Robb\nStark', False, 'newline character in value'],
        ['@0:NAME=Robb\rStark', False, 'return character in value'],
        ['@0:NAME=Robb\tStark', False, 'tab character in value'],
        ['@0:NAME=Robb\fStark', False, 'form feed character in value'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_blockprofile_message(self, message, expected, description):
        print description
        assert validators.valid_blockprofile_message(message) == expected

    @pytest.mark.parametrize('text, expected, description', [
        ['qsddsqfazer', True, 'valid text'],
        [123456, False, 'invalid text'],
        ['', True, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_text(self, text, expected, description):
        print description
        assert validators.valid_text(text) == expected

    @pytest.mark.parametrize('url, expected, description', [
        ['http://www.valyrian.tech', True, 'valid url'],
        ['www.valyrian.tech', True, 'valid url'],
        ['http://foo.com/blah_blah', True, 'valid url'],
        ['http://foo.com/blah_blah/', True, 'valid url'],
        ['http://foo.com/blah_blah_(wikipedia)', True, 'valid url'],
        ['http://foo.com/blah_blah_(wikipedia)_(again)', True, 'valid url'],
        ['http://www.example.com/wpstyle/?p=364', True, 'valid url'],
        ['https://www.example.com/foo/?bar=baz&inga=42&quux', True, 'valid url'],
        ['http://userid:password@example.com:8080', True, 'valid url'],
        ['http://userid:password@example.com:8080/ 	', True, 'valid url'],
        ['http://userid@example.com', True, 'valid url'],
        ['http://userid@example.com/', True, 'valid url'],
        ['http://userid@example.com:8080', True, 'valid url'],
        ['http://userid@example.com:8080/', True, 'valid url'],
        ['http://userid:password@example.com', True, 'valid url'],
        ['http://userid:password@example.com/', True, 'valid url'],
        ['http://142.42.1.1/', True, 'valid url'],
        ['http://142.42.1.1:8080/', True, 'valid url'],
        ['http://foo.com/blah_(wikipedia)#cite-1', True, 'valid url'],
        ['http://foo.com/(something)?after=parens', True, 'valid url'],
        ['http://code.google.com/events/#&product=browser', True, 'valid url'],
        ['http://foo.bar/?q=Test%20URL-encoded%20stuff', True, 'valid url'],
        ["http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com", True, 'valid url'],
        ['http://1337.net', True, 'valid url'],
        ['http://a.b-c.de', True, 'valid url'],
        ['http://223.255.255.254', True, 'valid url'],
        ['http://', False, 'invalid url'],
        # ['http://.', False, 'invalid url'],
        # ['http://..', False, 'invalid url'],
        # ['http://foo.bar?q=Spaces should be encoded', False, 'spaces should be encoded'],
        ['http:// shouldfail.com', False, 'invalid url'],
        ['www.google.com', True, 'valid url'],
        [123456, False, 'invalid url'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_url(self, url, expected, description):
        print description
        assert validators.valid_url(url) == expected

    @pytest.mark.parametrize('text, expected, description', [
        ['Wouter Glorieux', True, 'valid creator'],
        [123456, False, 'invalid creator'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_creator(self, text, expected, description):
        print description
        assert validators.valid_creator(text) == expected

    @pytest.mark.parametrize('email, expected, description', [
        ['info@valyrian.tech', True, 'valid email'],
        ['infovalyrian.tech', False, 'invalid email, no @'],
        ['info@valyriantech', False, 'invalid email, no . in domain'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_email(self, email, expected, description):
        print description
        assert validators.valid_email(email) == expected

    @pytest.mark.parametrize('amount, expected, description', [
        [0, True, 'valid amount: 0'],
        [1, True, 'valid amount: 1'],
        [-1, False, 'negative amount'],
        [1.5, False, 'floating point number'],
        ['a', False, 'string'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_amount(self, amount, expected, description):
        print description
        assert validators.valid_amount(amount) == expected

    @pytest.mark.parametrize('block_height, expected, description', [
        [0, True, 'valid block_height: 0'],
        [1, True, 'valid block_height: 1'],
        [350000, True, 'valid block_height: 350000'],
        [-1, False, 'negative number'],
        [1.5, False, 'floating point number'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_block_height(self, block_height, expected, description):
        print description
        assert validators.valid_block_height(block_height) == expected

    @pytest.mark.parametrize('percentage, expected, description', [
        [0, True, 'valid percentage: 0'],
        [1, True, 'valid percentage: 1'],
        [50, True, 'valid percentage: 50'],
        [100, True, 'valid percentage: 100'],
        [-1, False, 'negative number'],
        [100.1, False, 'higher than 100'],
        [1.5, True, 'floating point number'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_percentage(self, percentage, expected, description):
        print description
        assert validators.valid_percentage(percentage) == expected

    @pytest.mark.parametrize('url, expected, description', [
        ['http://youtu.be/C0DPdy98e4c', True, 'valid youtube id'],
        ['http://www.youtube.com/watch?v=lK-zaWCp-co&feature=g-all-u&context=G27a8a4aFAAAAAAAAAAA', True, 'valid youtube id'],
        ['http://youtu.be/AXaoi6dz59A', True, 'valid youtube id'],
        ['youtube.com/watch?gl=NL&hl=nl&feature=g-vrec&context=G2584313RVAAAAAAAABA&v=35LqQPKylEA', True, 'valid youtube id'],
        ['https://youtube.com/watch?gl=NL&hl=nl&feature=g-vrec&context=G2584313RVAAAAAAAABA&v=35LqQPKylEA', True, 'valid youtube id'],
        [0, False, 'invalid id'],
        ['', False, 'empty string'],
        ['www.youtube.com', False, 'no video id'],
        ['http://www.mytube.com/watch?v=35LqQPKylEA', False, 'mytube.com'],
        [None, False, 'None value'],
    ])
    def test_valid_youtube(self, url, expected, description):
        print description
        assert validators.valid_youtube(url) == expected

    @pytest.mark.parametrize('url, expected, description', [
        ['C0DPdy98e4c', True, 'valid youtube id'],
        ['C0DPdy98e4', False, 'too short'],
        ['C0DPdy98e4c1', False, 'too long'],
        [0, False, 'invalid id'],
        ['', False, 'empty string'],
        ['www.youtube.com', False, 'no video id'],
        [None, False, 'None value'],
    ])
    def test_valid_youtube_id(self, url, expected, description):
        print description
        assert validators.valid_youtube_id(url) == expected

    @pytest.mark.parametrize('key, expected, description', [
        ['KyH94vd8icQJ67aqqLRT5p33YFtYSgkGTdMWYA2suZaNJrjxNnFY', True, 'valid private key'],
        ['KwWu5FynetG6q8n7kzEmgdGtx3F5J9fQhvukQb9mCXCTpyzjoVtk', True, 'valid private key'],
        ['L4BgVKq9nibtSKsWyRMBrx78DnYVQNNzYNegtp4n2mtUZigA6a5P', True, 'valid private key'],
        ['L2ZC36oFWRvxqrD8PL6KCfM2zTjB4Z5bEdKmuqhbtLFg1c2a7xHg', True, 'valid private key'],
        ['5K2QLxgw38v1RD4CeEPW3eEbtXygSGstFsNUPr6aHAM6DRND1mW', True, 'valid private key'],
        [0, False, 'invalid private key: 0'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_private_key(self, key, expected, description):
        print description
        assert validators.valid_private_key(key) == expected

    @pytest.mark.parametrize('distribution, expected, description', [
        [{u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y': 100000,
          u'1SansacmMr38bdzGkzruDVajEsZuiZHx9': 400000,
          u'1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8': 500000}, True, 'valid distribution'],

        [{u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y': 'a',
          u'1SansacmMr38bdzGkzruDVajEsZuiZHx9': 400000,
          u'1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8': 500000}, False, 'value not a integer'],

        [{u'4Robbk6PuJst6ot6ay2DcVugv8nxfJh5y': 100000,
          u'1SansacmMr38bdzGkzruDVajEsZuiZHx9': 400000,
          u'1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8': 500000}, False, 'address not valid'],

        [{}, False, 'empty dict'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_distribution(self, distribution, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=False)
        print description
        assert validators.valid_distribution(distribution) == expected

    @pytest.mark.parametrize('outputs, expected, description', [
        [[('1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 50000), ('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 50000)], True, 'valid outputs'],
        [[('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 50000)], True, 'valid outputs'],
        [[('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 'q')], False, 'invalid outputs: second parameter not an integer'],
        ['', False, 'empty string'],
        [None, False, 'None value'],
    ])
    def test_valid_outputs(self, outputs, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=False)
        print description
        assert validators.valid_outputs(outputs) == expected

    @pytest.mark.parametrize('address, expected, description', [
        ["BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4", True, "Valid bech32 address"],
        ["bc1pw508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7k7grplx", True, "Valid bech32 address"],
        ["BC1SW50QA3JX3S", True, "Valid bech32 address"],
        ["bc1zw508d6qejxtdg4y5r3zarvaryvg6kdaj", True, "Valid bech32 address"],

        ["tc1qw508d6qejxtdg4y5r3zarvary0c5xw7kg3g4ty", False, "Invalid human-readable part"],
        ["bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5", False, "Invalid checksum"],
        # ["BC13W508D6QEJXTDG4Y5R3ZARVARY0C5XW7KN40WF2",False, "Invalid witness version"],
        ["bc1rw5uspcuh", False, "Invalid program length"],
        ["bc10w508d6qejxtdg4y5r3zarvary0c5xw7kw508d6qejxtdg4y5r3zarvary0c5xw7kw5rljs90", False, "Invalid program length"],
        # ["BC1QR508D6QEJXTDG4Y5R3ZARVARYV98GJ9P", False, "Invalid program length for witness version 0 (per BIP141)"],
        # ["bc1zw508d6qejxtdg4y5r3zarvaryvqyzf3du", False, "zero padding of more than 4 bits"],
        ["bc1gmk9yu", False, "Empty data section"],
    ])
    def test_valid_bech32_address_mainnet(self, address, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=False)
        print description
        assert validators.valid_bech32_address(address) == expected

    @pytest.mark.parametrize('address, expected, description', [
        ["tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7", True, "Valid bech32 address"],
        ["tb1qqqqqp399et2xygdj5xreqhjjvcmzhxw4aywxecjdzew6hylgvsesrxh6hy", True, "Valid bech32 address"],

        ["tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sL5k7", False, "Mixed case"],
        # ["tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3pjxtptv", False, "Non-zero padding in 8-to-5 conversion"],
    ])
    def test_valid_bech32_address_testnet(self, address, expected, description):
        helpers.configurationhelpers.get_use_testnet = mock.MagicMock(return_value=True)
        print description
        assert validators.valid_bech32_address(address) == expected
