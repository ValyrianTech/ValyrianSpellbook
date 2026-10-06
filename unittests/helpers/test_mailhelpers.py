#!/usr/bin/env python
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestLoadSmtpSettings(unittest.TestCase):
    """Test cases for load_smtp_settings function"""

    @patch('helpers.mailhelpers.get_smtp_from_address', return_value='from@test.com')
    @patch('helpers.mailhelpers.get_smtp_host', return_value='smtp.test.com')
    @patch('helpers.mailhelpers.get_smtp_port', return_value=587)
    @patch('helpers.mailhelpers.get_smtp_user', return_value='user')
    @patch('helpers.mailhelpers.get_smtp_password', return_value='password')
    def test_load_smtp_settings(self, mock_pass, mock_user, mock_port, mock_host, mock_from):
        """Test loading SMTP settings from configuration"""
        import helpers.mailhelpers as mail_module
        from helpers.mailhelpers import load_smtp_settings
        
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
        from helpers.mailhelpers import sendmail
        
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
                mock_smtp.side_effect = ValueError('Connection failed')
                
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

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_attachment_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail when attachment file cannot be read - should log error but still send"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            template_path = os.path.join(temp_dir, 'test_template.txt')
            with open(template_path, 'w') as f:
                f.write('Test content')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    attachments={'doc.pdf': '/nonexistent/path.pdf'}
                )

                # Should still succeed, just log error for attachment
                self.assertTrue(result)
                mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_with_both_html_and_txt_templates(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with both HTML and txt templates available"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create both templates
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Plain text content')
            html_path = os.path.join(temp_dir, 'test_template.html')
            with open(html_path, 'w') as f:
                f.write('<html><body>HTML content</body></html>')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template'
                )

                self.assertTrue(result)
                mock_session.sendmail.assert_called_once()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_template_in_apps_dir(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail finds template in apps directory (lines 85, 90)"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as template_dir, tempfile.TemporaryDirectory() as apps_dir:
            # Create templates only in apps dir, not template dir
            html_path = os.path.join(apps_dir, 'app_template.html')
            with open(html_path, 'w') as f:
                f.write('<html>Test</html>')
            txt_path = os.path.join(apps_dir, 'app_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', template_dir), \
                 patch('helpers.mailhelpers.APPS_DIR', apps_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='app_template'
                )
                
                self.assertTrue(result)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_html_template_read_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail with HTML template read error (lines 101-103)"""
        from helpers.mailhelpers import sendmail
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a valid txt template
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')
            
            # Create an html template path that exists but can't be read
            html_path = os.path.join(temp_dir, 'test_template.html')
            with open(html_path, 'w') as f:
                f.write('<html>Test</html>')
            
            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session
                
                # Mock open to raise for the html file
                original_open = open
                def mock_open_func(path, *args, **kwargs):
                    if 'test_template.html' in str(path):
                        raise PermissionError('Permission denied')
                    return original_open(path, *args, **kwargs)
                
                with patch('builtins.open', side_effect=mock_open_func):
                    result = sendmail(
                        recipients='test@example.com',
                        subject='Test Subject',
                        body_template='test_template'
                    )
                    
                    self.assertFalse(result)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    def test_sendmail_none_recipients(self, mock_log, mock_load, mock_enable):
        """Test sendmail rejects a None recipients argument"""
        from helpers.mailhelpers import sendmail

        result = sendmail(None, 'Subject', 'test_template')

        self.assertFalse(result)
        mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    def test_sendmail_invalid_recipients(self, mock_log, mock_load, mock_enable):
        """Test sendmail rejects an invalid email address"""
        from helpers.mailhelpers import sendmail

        result = sendmail('not-an-email', 'Subject', 'test_template')

        self.assertFalse(result)
        mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    def test_sendmail_path_traversal_template_rejected(self, mock_log, mock_load, mock_enable):
        """Test sendmail rejects a body_template that escapes the template directories"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir, \
             patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
             patch('helpers.mailhelpers.APPS_DIR', temp_dir):
            result = sendmail(
                recipients='test@example.com',
                subject='Test Subject',
                body_template='../../etc/passwd'
            )

            self.assertFalse(result)
            mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_image_path_traversal_rejected_but_sends(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail rejects an image path escaping the allowed dirs but still sends"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                 patch('helpers.mailhelpers.IMAGE_DIRS', [temp_dir]):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    images={'logo': '../../etc/passwd'}
                )

                self.assertTrue(result)
                mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_attachment_path_traversal_rejected_but_sends(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail rejects an attachment path escaping the allowed dirs but still sends"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                 patch('helpers.mailhelpers.ATTACHMENT_DIRS', [temp_dir]):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    attachments={'secret.txt': '../../etc/passwd'}
                )

                self.assertTrue(result)
                mock_log.error.assert_called()

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_image_within_template_dir_attaches(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail attaches an image resolved within TEMPLATE_DIR"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = os.path.join(temp_dir, 'test_template.html')
            with open(html_path, 'w') as f:
                f.write('<html><body><img src="cid:logo"></body></html>')

            image_path = os.path.join(temp_dir, 'logo.png')
            with open(image_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                 patch('helpers.mailhelpers.IMAGE_DIRS', [temp_dir]):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    images={'logo': 'logo.png'}
                )

                self.assertTrue(result)
                sent_message = mock_session.sendmail.call_args[0][2]
                self.assertIn('Content-ID: <logo>', sent_message)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_attachment_within_template_dir_attaches(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail attaches an attachment resolved within TEMPLATE_DIR"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')

            attachment_path = os.path.join(temp_dir, 'document.pdf')
            with open(attachment_path, 'wb') as f:
                f.write(b'%PDF-1.4')

            with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                 patch('helpers.mailhelpers.ATTACHMENT_DIRS', [temp_dir]):
                mock_session = MagicMock()
                mock_smtp.return_value = mock_session

                result = sendmail(
                    recipients='test@example.com',
                    subject='Test Subject',
                    body_template='test_template',
                    attachments={'document.pdf': 'document.pdf'}
                )

                self.assertTrue(result)
                sent_message = mock_session.sendmail.call_args[0][2]
                self.assertIn('document.pdf', sent_message)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_image_open_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail logs an error when a resolvable image fails to open but still sends"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')

            image_path = os.path.join(temp_dir, 'logo.png')
            with open(image_path, 'wb') as f:
                f.write(b'\x89PNG\r\n\x1a\n')
            os.chmod(image_path, 0o000)

            try:
                with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                     patch('helpers.mailhelpers.IMAGE_DIRS', [temp_dir]):
                    mock_session = MagicMock()
                    mock_smtp.return_value = mock_session

                    result = sendmail(
                        recipients='test@example.com',
                        subject='Test Subject',
                        body_template='test_template',
                        images={'logo': 'logo.png'}
                    )

                    self.assertTrue(result)
                    mock_log.error.assert_called()
            finally:
                os.chmod(image_path, 0o644)

    @patch('helpers.mailhelpers.get_enable_smtp', return_value=True)
    @patch('helpers.mailhelpers.load_smtp_settings')
    @patch('helpers.mailhelpers.LOG')
    @patch('helpers.mailhelpers.smtplib.SMTP')
    def test_sendmail_attachment_open_error(self, mock_smtp, mock_log, mock_load, mock_enable):
        """Test sendmail logs an error when a resolvable attachment fails to open but still sends"""
        from helpers.mailhelpers import sendmail

        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, 'test_template.txt')
            with open(txt_path, 'w') as f:
                f.write('Test content')

            attachment_path = os.path.join(temp_dir, 'document.pdf')
            with open(attachment_path, 'wb') as f:
                f.write(b'%PDF-1.4')
            os.chmod(attachment_path, 0o000)

            try:
                with patch('helpers.mailhelpers.TEMPLATE_DIR', temp_dir), \
                     patch('helpers.mailhelpers.ATTACHMENT_DIRS', [temp_dir]):
                    mock_session = MagicMock()
                    mock_smtp.return_value = mock_session

                    result = sendmail(
                        recipients='test@example.com',
                        subject='Test Subject',
                        body_template='test_template',
                        attachments={'document.pdf': 'document.pdf'}
                    )

                    self.assertTrue(result)
                    mock_log.error.assert_called()
            finally:
                os.chmod(attachment_path, 0o644)


class TestResolveWithin(unittest.TestCase):
    """Test cases for the _resolve_within helper"""

    def test_resolve_within_success(self):
        """Test _resolve_within returns the real path for a file inside root"""
        from helpers.mailhelpers import _resolve_within

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'template.html')
            with open(file_path, 'w') as f:
                f.write('content')

            result = _resolve_within(temp_dir, 'template', '.html')
            self.assertEqual(result, os.path.realpath(file_path))

    def test_resolve_within_escape(self):
        """Test _resolve_within returns None when the path escapes root"""
        from helpers.mailhelpers import _resolve_within

        with tempfile.TemporaryDirectory() as temp_dir:
            result = _resolve_within(temp_dir, '../outside', '.html')
            self.assertIsNone(result)

    def test_resolve_within_commonpath_valueerror(self):
        """Test _resolve_within returns None when commonpath raises ValueError"""
        from helpers.mailhelpers import _resolve_within

        with patch('os.path.commonpath', side_effect=ValueError('mixed paths')):
            result = _resolve_within('/tmp', 'test')
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
