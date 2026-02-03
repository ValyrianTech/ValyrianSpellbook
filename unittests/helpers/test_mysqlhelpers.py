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

    @patch('helpers.mysqlhelpers.LOG')
    def test_mysql_cursor_with_commit(self, mock_log):
        """Test mysql_cursor with commit=True"""
        import helpers.mysqlhelpers as mysql_module
        
        mock_cnx = MagicMock()
        mock_cursor_obj = MagicMock()
        mock_cnx.cursor.return_value = mock_cursor_obj
        
        with patch.object(mysql_module.mysql.connector, 'connect', return_value=mock_cnx):
            from helpers.mysqlhelpers import mysql_cursor
            
            with mysql_cursor('user', 'pass', 'db', commit=True) as cursor:
                pass
            
            mock_cnx.commit.assert_called_once()

    def test_create_database_error(self):
        """Test database creation error handling - should not raise"""
        import mysql.connector
        from helpers.mysqlhelpers import create_database
        
        mock_cursor = MagicMock()
        # Create a real mysql.connector.Error exception
        mock_cursor.execute.side_effect = mysql.connector.Error("Database exists")
        
        # Should not raise - error is caught and logged
        create_database(mock_cursor, 'test_db')
        
        # Verify execute was called
        mock_cursor.execute.assert_called_once()

    @patch('helpers.mysqlhelpers.LOG')
    def test_create_tables_success(self, mock_log):
        """Test successful table creation"""
        from helpers.mysqlhelpers import create_tables
        
        mock_cursor = MagicMock()
        tables = {
            'users': 'CREATE TABLE users (id INT)',
            'posts': 'CREATE TABLE posts (id INT)'
        }
        
        create_tables(mock_cursor, tables)
        
        self.assertEqual(mock_cursor.execute.call_count, 2)

    @patch('helpers.mysqlhelpers.LOG')
    def test_create_tables_already_exists(self, mock_log):
        """Test table creation when table already exists"""
        import helpers.mysqlhelpers as mysql_module
        from helpers.mysqlhelpers import create_tables
        
        mock_cursor = MagicMock()
        
        # Create an error with ER_TABLE_EXISTS_ERROR errno
        mock_error = MagicMock()
        mock_error.errno = mysql_module.mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR
        mock_error.msg = "Table already exists"
        mock_cursor.execute.side_effect = mock_error
        
        tables = {'users': 'CREATE TABLE users (id INT)'}
        
        create_tables(mock_cursor, tables)
        
        # Should log "already exists" info, not error
        mock_log.info.assert_called()

    def test_create_tables_other_error(self):
        """Test table creation with other errors - should not raise"""
        import mysql.connector
        from helpers.mysqlhelpers import create_tables
        
        mock_cursor = MagicMock()
        
        # Create a real mysql.connector.Error with a different errno
        error = mysql.connector.Error("Some other error")
        error.errno = 1234  # Some other error (not ER_TABLE_EXISTS_ERROR)
        error.msg = "Some other error"
        mock_cursor.execute.side_effect = error
        
        tables = {'users': 'CREATE TABLE users (id INT)'}
        
        # Should not raise - error is caught and logged
        create_tables(mock_cursor, tables)
        
        # Verify execute was called
        mock_cursor.execute.assert_called_once()

    @patch('helpers.mysqlhelpers.create_tables')
    @patch('helpers.mysqlhelpers.create_database')
    @patch('helpers.mysqlhelpers.LOG')
    def test_initialize_database_exists(self, mock_log, mock_create_db, mock_create_tables):
        """Test initialize_database when database exists"""
        import helpers.mysqlhelpers as mysql_module
        from helpers.mysqlhelpers import initialize_database
        
        mock_cnx = MagicMock()
        mock_cursor = MagicMock()
        mock_cnx.cursor.return_value = mock_cursor
        
        with patch.object(mysql_module.mysql.connector, 'connect', return_value=mock_cnx):
            initialize_database('test_db', {}, 'user', 'pass')
        
        mock_cursor.execute.assert_called_with("USE {}".format('test_db'))
        mock_cursor.close.assert_called_once()
        mock_cnx.close.assert_called_once()



if __name__ == '__main__':
    unittest.main()
