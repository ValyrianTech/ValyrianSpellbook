#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open


class TestLoadSmtpSettings(unittest.TestCase):
    """Test cases for load_smtp_settings function"""

    @patch('helpers.mailhelpers.get_smtp_from_address', return_value='from@test.com')
    @patch('helpers.mailhelpers.get_smtp_host', return_value='smtp.test.com')
    @patch('helpers.mailhelpers.get_smtp_port', return_value=587)
    @patch('helpers.mailhelpers.get_smtp_user', return_value='user')
    @patch('helpers.mailhelpers.get_smtp_password', return_value='password')
    def test_load_smtp_settings(self, mock_pass, mock_user, mock_port, mock_host, mock_from):
        """Test loading SMTP settings from configuration"""
        from helpers.mailhelpers import load_smtp_settings
        import helpers.mailhelpers as mail_module
        
        load_smtp_settings()
        
        self.assertEqual(mail_module.FROM_ADDRESS, 'from@test.com')
        self.assertEqual(mail_module.HOST, 'smtp.test.com')
        self.assertEqual(mail_module.PORT, 587)
        self.assertEqual(mail_module.USER, 'user')
        self.assertEqual(mail_module.PASSWORD, 'password')


class TestSendmail(unittest.TestCase):
    """Test cases for sendmail function"""

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=False)
    @patch('helpers.mailhelpers.LOG')
    def test_sendmail_smtp_disabled(self, mock_log, mock_enable):
        """Test sendmail when SMTP is disabled"""
        from helpers.mailhelpers import sendmail
        
        result = sendmail('test@example.com', 'Subject', 'template')
        
        self.assertTrue(result)
        mock_log.warning.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('os.path.isfile', return_value=False)
    def test_sendmail_template_not_found(self, mock_isfile, mock_log, mock_load, mock_enable):
        """Test sendmail when template is not found"""
        from helpers.mailhelpers import sendmail
        
        result = sendmail('test@example.com', 'Subject', 'nonexistent_template')
        
        self.assertFalse(result)
        mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_txt_template(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with txt template"""
        from helpers.mailhelpers import sendmail, TEMPLATE_DIR
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary template file
            template_content = 'Hello $NAME$, this is a test.'
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            # Patch TEMPLATE_DIR
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    variables={'NAME': 'John'}
                )
                
                self.assertTrue(result)
                mock_session.sendmail.assert_called_once()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_html_template(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with html template"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_content = '<html><body>Hello $NAME$</body></html>'
            template_path = os.path.join(temp_dir, 'test_template.html')
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    variables={'NAME': 'John'}
                )
                
                self.assertTrue(result)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_smtp_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail when SMTP connection fails"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write('Test content')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_smtp.side_effect = Exception('Connection failed')
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template'
                )
                
                self.assertFalse(result)
                mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_images(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with embedded images"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template
            template_path = os.path.join(temp_dir, 'test_template.html')
            with open(template_path, 'w') as f:
                f.write('<html><body><img src="cid:logo"></body></html>')
            
            # Create image file
            image_path = os.path.join(temp_dir, 'logo.png')
            with open(image_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')  # PNG header
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    images={'logo': image_path}
                )
                
                self.assertTrue(result)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_image_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with image that fails to load"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'test_template.html')
            with open(template_path, 'w') as f:
                f.write('<html><body>Test</body></html>')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    images={'logo': '/nonexistent/path.png'}
                )
                
                # Should still succeed, just log error for image
                self.assertTrue(result)
                mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_attachments(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with attachments"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write('Test content')
            
            # Create attachment file
            attachment_path = os.path.join(temp_dir, 'document.pdf')
            with open(attachment_path, 'wb') as f:
                f.write(b'%PDF-1.4')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    attachments={'document.pdf': attachment_path}
                )
                
                self.assertTrue(result)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_multiple_recipients(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with multiple recipients"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write('Test content')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test1@example.com,test2@example.com',
                    subject='Test Subject',
                    body_template='test_template'
                )
                
                self.assertTrue(result)
                # Check that sendmail was called with list of recipients
                call_args = mock_session.sendmail.call_args
                self.assertEqual(call_args[0][1], ['test1@example.com', 'test2@example.com'])

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    def test_sendmail_template_read_error(self, mock_log, mock_load, mock_enable):
        """Test sendmail when template file cannot be read"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write('Test content')
            
            # Make file unreadable
            os.chmod(template_path, 0o000)
            
            try:
                with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                    result = sendmail(
                        recipients='test@example.com',
                        subject='Test Subject',
                        body_template='test_template'
                    )
                    
                    self.assertFalse(result)
            finally:
                # Restore permissions for cleanup
                os.chmod(template_path, 0o644)


class TestModuleConstants(unittest.TestCase):
    """Test module constants"""

    def test_template_dir_exists(self):
        """Test that TEMPLATE_DIR is set"""
        from helpers.mailhelpers import TEMPLATE_DIR
        self.assertIsNotNone(TEMPLATE_DIR)

    def test_apps_dir_exists(self):
        """Test that APPS_DIR is set"""
        from helpers.mailhelpers import APPS_DIR
        self.assertIsNotNone(APPS_DIR)

    def test_port_is_integer(self):
        """Test PORT is an integer"""
        from helpers.mailhelpers import PORT
        self.assertIsInstance(PORT, int)


if __name__ == '__main__':
    unittest.main()
