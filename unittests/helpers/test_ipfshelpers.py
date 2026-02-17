#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock


class TestCheckIpfs(unittest.TestCase):
    """Test cases for check_ipfs function"""

    @patch('helpers.ipfshelpers.get_ipfs_api_host', return_value='localhost')
    @patch('helpers.ipfshelpers.get_ipfs_api_port', return_value=5001)
    @patch('helpers.ipfshelpers.connect')
    def test_check_ipfs_success(self, mock_connect, mock_port, mock_host):
        """Test check_ipfs when IPFS is running"""
        from helpers.ipfshelpers import check_ipfs
        
        result = check_ipfs()
        
        self.assertTrue(result)
        mock_connect.assert_called_once_with(host='localhost', port=5001)

    @patch('helpers.ipfshelpers.get_ipfs_api_host', return_value='localhost')
    @patch('helpers.ipfshelpers.get_ipfs_api_port', return_value=5001)
    @patch('helpers.ipfshelpers.connect')
    @patch('helpers.ipfshelpers.LOG')
    def test_check_ipfs_failure(self, mock_log, mock_connect, mock_port, mock_host):
        """Test check_ipfs when IPFS is not running"""
        from helpers.ipfshelpers import check_ipfs
        
        mock_connect.side_effect = Exception('Connection refused')
        
        result = check_ipfs()
        
        self.assertFalse(result)
        mock_log.error.assert_called()


class TestAddJson(unittest.TestCase):
    """Test cases for add_json function"""

    @patch('helpers.ipfshelpers.IPFSDict')
    def test_add_json(self, mock_ipfs_dict_class):
        """Test add_json function"""
        from helpers.ipfshelpers import add_json
        
        mock_ipfs_dict = MagicMock()
        mock_ipfs_dict.save.return_value = 'QmTestHash123'
        mock_ipfs_dict_class.return_value = mock_ipfs_dict
        
        data = {'key1': 'value1', 'key2': 'value2'}
        result = add_json(data)
        
        self.assertEqual(result, 'QmTestHash123')
        mock_ipfs_dict.save.assert_called_once()

    @patch('helpers.ipfshelpers.IPFSDict')
    def test_add_json_empty_dict(self, mock_ipfs_dict_class):
        """Test add_json with empty dictionary"""
        from helpers.ipfshelpers import add_json
        
        mock_ipfs_dict = MagicMock()
        mock_ipfs_dict.save.return_value = 'QmEmptyHash'
        mock_ipfs_dict_class.return_value = mock_ipfs_dict
        
        result = add_json({})
        
        self.assertEqual(result, 'QmEmptyHash')


class TestGetJson(unittest.TestCase):
    """Test cases for get_json function"""

    @patch('helpers.ipfshelpers.IPFSDict')
    def test_get_json(self, mock_ipfs_dict_class):
        """Test get_json function"""
        from helpers.ipfshelpers import get_json
        
        mock_ipfs_dict = MagicMock()
        mock_ipfs_dict.items.return_value = [('key1', 'value1'), ('key2', 'value2')]
        mock_ipfs_dict_class.return_value = mock_ipfs_dict
        
        result = get_json('QmTestHash123')
        
        mock_ipfs_dict_class.assert_called_once_with(cid='QmTestHash123')


class TestFileMetaData(unittest.TestCase):
    """Test cases for FileMetaData class"""

    def test_file_metadata_attributes(self):
        """Test FileMetaData attribute assignment"""
        from helpers.ipfshelpers import FileMetaData
        
        metadata = FileMetaData()
        metadata.file_name = 'test.pdf'
        metadata.file_ipfs_hash = 'QmHash123'
        metadata.file_sha256_hash = 'sha256hash'
        metadata.file_size = 1024
        metadata.txid = 'txid123'
        metadata.publisher_name = 'Test Publisher'
        metadata.publisher_address = '1BitcoinAddress'
        metadata.publisher_signature = 'signature'
        metadata.signed_message = 'message'
        
        self.assertEqual(metadata.file_name, 'test.pdf')
        self.assertEqual(metadata.file_ipfs_hash, 'QmHash123')
        self.assertEqual(metadata.file_sha256_hash, 'sha256hash')
        self.assertEqual(metadata.file_size, 1024)
        self.assertEqual(metadata.txid, 'txid123')
        self.assertEqual(metadata.publisher_name, 'Test Publisher')
        self.assertEqual(metadata.publisher_address, '1BitcoinAddress')
        self.assertEqual(metadata.publisher_signature, 'signature')
        self.assertEqual(metadata.signed_message, 'message')


class TestAddFile(unittest.TestCase):
    """Test cases for add_file function"""

    @patch('helpers.ipfshelpers.IPFS_API')
    def test_add_file_success(self, mock_ipfs_api):
        """Test add_file function success"""
        # We need to set the global IPFS_API in the module
        import helpers.ipfshelpers as ipfs_module
        
        mock_api = MagicMock()
        mock_api.add.return_value = {
            'Hash': 'QmTestHash123',
            'Name': 'testfile.txt',
            'Size': '1024'
        }
        ipfs_module.IPFS_API = mock_api
        
        from helpers.ipfshelpers import add_file
        
        result = add_file('testfile.txt')
        
        self.assertEqual(result[0], 'QmTestHash123')
        self.assertEqual(result[1], 'testfile.txt')
        self.assertEqual(result[2], '1024')

    @patch('helpers.ipfshelpers.LOG')
    def test_add_file_failure(self, mock_log):
        """Test add_file function failure"""
        import helpers.ipfshelpers as ipfs_module
        
        mock_api = MagicMock()
        mock_api.add.side_effect = Exception('IPFS connection failed')
        ipfs_module.IPFS_API = mock_api
        
        from helpers.ipfshelpers import add_file
        
        with self.assertRaises(Exception) as context:
            add_file('testfile.txt')
        
        self.assertIn('IPFS failure', str(context.exception))
        mock_log.error.assert_called()


if __name__ == '__main__':
    unittest.main()
