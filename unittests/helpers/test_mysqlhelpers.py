#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import unittest
from unittest.mock import patch, MagicMock

# Create mock for mysql.connector before importing the module
mock_mysql_connector = MagicMock()
sys.modules['mysql'] = MagicMock()
sys.modules['mysql.connector'] = mock_mysql_connector


class TestMysqlHelpers(unittest.TestCase):
    """Test cases for helpers/mysqlhelpers.py
    
    Note: These tests mock the mysql.connector module to avoid
    requiring a MySQL installation.
    """

    @patch('helpers.mysqlhelpers.LOG')
    def test_create_database_success(self, mock_log):
        """Test successful database creation"""
        from helpers.mysqlhelpers import create_database
        
        mock_cursor = MagicMock()
        
        create_database(mock_cursor, 'test_db')
        
        mock_cursor.execute.assert_called_once()
        self.assertIn('test_db', mock_cursor.execute.call_args[0][0])

    @patch('helpers.mysqlhelpers.LOG')
    def test_log_sql_query(self, mock_log):
        """Test SQL query logging"""
        from helpers.mysqlhelpers import log_sql_query
        
        sql = "SELECT * FROM users\nWHERE id = 1"
        
        log_sql_query(sql)
        
        # Should log begin, each line, and end
        self.assertGreaterEqual(mock_log.info.call_count, 3)

    def test_mysql_cursor_init(self):
        """Test mysql_cursor initialization"""
        from helpers.mysqlhelpers import mysql_cursor
        
        cursor = mysql_cursor(
            user='test_user',
            password='test_pass',
            database='test_db',
            host='127.0.0.1',
            port=3306,
            commit=True
        )
        
        self.assertEqual(cursor.user, 'test_user')
        self.assertEqual(cursor.password, 'test_pass')
        self.assertEqual(cursor.database, 'test_db')
        self.assertEqual(cursor.host, '127.0.0.1')
        self.assertEqual(cursor.port, 3306)
        self.assertTrue(cursor.commit)

    @patch('helpers.mysqlhelpers.LOG')
    def test_mysql_cursor_context_manager(self, mock_log):
        """Test mysql_cursor as context manager"""
        import helpers.mysqlhelpers as mysql_module
        
        mock_cnx = MagicMock()
        mock_cursor_obj = MagicMock()
        mock_cnx.cursor.return_value = mock_cursor_obj
        
        # Patch the mysql.connector.connect at the module level
        with patch.object(mysql_module.mysql.connector, 'connect', return_value=mock_cnx):
            from helpers.mysqlhelpers import mysql_cursor
            
            with mysql_cursor('user', 'pass', 'db') as cursor:
                self.assertEqual(cursor, mock_cursor_obj)
            
            mock_cursor_obj.close.assert_called_once()
            mock_cnx.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
