#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
import sys
import time
import traceback
import uuid
import magic
from configparser import ConfigParser
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler

from bottle import Bottle, request, response, static_file, ServerAdapter, server_names, HTTPResponse

from authentication import initialize_api_keys_file
from data.data import get_explorers, get_explorer_config, save_explorer, delete_explorer
from data.data import latest_block, block_by_height, block_by_hash, prime_input_address, transaction
from data.data import transactions, balance, utxos
from decorators import authentication_required, use_explorer, output_json
from helpers.actionhelpers import get_actions, get_action_config, save_action, delete_action, run_action, get_reveal
from helpers.configurationhelpers import get_host, get_port, get_notification_email, get_mail_on_exception, what_is_my_ip
from helpers.configurationhelpers import get_enable_uploads, get_uploads_dir, get_allowed_extensions, get_max_file_size
from helpers.configurationhelpers import get_enable_transcribe, get_allowed_extensions_transcribe, get_max_file_size_transcribe, get_model_size_transcribe
from helpers.configurationhelpers import get_enable_ssl, get_ssl_certificate, get_ssl_private_key, get_ssl_certificate_chain, get_enable_wallet
from helpers.hotwallethelpers import get_hot_wallet
from helpers.loghelpers import LOG, REQUESTS_LOG, get_logs
from helpers.triggerhelpers import get_triggers, get_trigger_config, save_trigger, delete_trigger, activate_trigger, \
    check_triggers, verify_signed_message, http_get_request, http_post_request, http_delete_request, http_options_request, sign_message, file_download
from helpers.mailhelpers import sendmail
from inputs.inputs import get_sil, get_profile, get_sul
from linker.linker import get_lal, get_lbl, get_lrl, get_lsl
from randomaddress.randomaddress import random_address_from_sil, random_address_from_lbl, random_address_from_lrl, \
    random_address_from_lsl
from helpers.qrhelpers import generate_qr
from helpers.llmhelpers import load_llms, get_llm_config, save_llm_config, delete_llm

# Make sure the current working directory is correct
PROGRAM_DIR = os.path.abspath(os.path.dirname(__file__))
os.chdir(PROGRAM_DIR)

# Only load the WhisperModel if transcribe endpoint is enabled
if get_enable_transcribe() is True:
    from faster_whisper import WhisperModel

    model_size_or_path = get_model_size_transcribe()
    model_size_or_path = model_size_or_path.replace('$programdir$', PROGRAM_DIR)
    LOG.info(f'Loading WhisperModel with model_size_or_path: {model_size_or_path}')
    WHISPER_MODEL = WhisperModel(model_size_or_path=model_size_or_path, device="cpu", compute_type="int8")

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Credentials'] = True
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, HEAD, authorization'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        return fn(*args, **kwargs)

    return _enable_cors


class SSLWebServer(ServerAdapter):
    """
    CherryPy web server with SSL support.
    """

    def run(self, handler):
        """
        Runs a CherryPy Server using the SSL certificate.
        """
        from cheroot.wsgi import Server as CherryPyWSGIServer
        from cheroot.ssl.builtin import BuiltinSSLAdapter

        server = CherryPyWSGIServer((self.host, self.port), handler)

        server.ssl_adapter = BuiltinSSLAdapter(
            certificate=get_ssl_certificate(),
            private_key=get_ssl_private_key(),
            certificate_chain=get_ssl_certificate_chain() if get_ssl_certificate_chain() != "" else None
        )

        try:
            server.start()
        except Exception as ex:
            LOG.error('Unable to start SSL server: %s' % ex)
            server.stop()


server_names['sslwebserver'] = SSLWebServer


class SpellbookRESTAPI(Bottle):
    def __init__(self):
        super(SpellbookRESTAPI, self).__init__()

        # Initialize variables
        self.host = get_host()
        self.port = get_port()

        # Log the requests to the REST API in a separate file by installing a custom LoggingPlugin
        self.install(self.log_to_logger)

        # Make sure that an api_keys.json file is present, the first time the server is started
        # a new random api key and secret pair will be generated
        if not os.path.isfile('json/private/api_keys.json'):
            LOG.info('Generating new API keys')
            initialize_api_keys_file()

        LOG.info('Starting Bitcoin Spellbook')

        try:
            if get_enable_wallet() is True:
                get_hot_wallet()
        except Exception as ex:
            LOG.error('Unable to decrypt hot wallet: %s' % ex)
            sys.exit(1)

        LOG.info('To make the server run in the background: use Control-Z, then use command: bg %1')

        # Initialize the routes for the REST API
        self.route('/', method='GET', callback=self.index)  # on linux this gets requested every minute or so, but not on windows
        self.route('/favicon.ico', method='GET', callback=self.get_favicon)

        # Route for ping, to test if server is online
        self.route('/spellbook/ping', method='GET', callback=self.ping)

        # Routes for managing blockexplorers
        self.route('/spellbook/explorers', method='GET', callback=self.get_explorers)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='POST', callback=self.save_explorer)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.get_explorer_config)
        self.route('/spellbook/explorers/<explorer_id:re:[a-zA-Z0-9_\-.]+>', method='DELETE', callback=self.delete_explorer)

        # Routes for managing LLMs
        self.route('/spellbook/llms', method='GET', callback=self.get_llms)
        self.route('/spellbook/llms', method='OPTIONS', callback=self.get_llms)
        self.route('/spellbook/llms/<llm_id:re:[a-zA-Z0-9_\-.:]+>', method='POST', callback=self.save_llm_config)
        self.route('/spellbook/llms/<llm_id:re:[a-zA-Z0-9_\-.:]+>', method='GET', callback=self.get_llm_config)
        self.route('/spellbook/llms/<llm_id:re:[a-zA-Z0-9_\-.:]+>', method='OPTIONS', callback=self.get_llm_config)
        self.route('/spellbook/llms/<llm_id:re:[a-zA-Z0-9_\-.:]+>', method='DELETE', callback=self.delete_llm)

        # Routes for retrieving data from the blockchain
        self.route('/spellbook/blocks/latest', method='GET', callback=self.get_latest_block)
        self.route('/spellbook/blocks/<height:int>', method='GET', callback=self.get_block_by_height)
        self.route('/spellbook/blocks/<block_hash:re:[a-f0-9]+>', method='GET', callback=self.get_block_by_hash)

        self.route('/spellbook/transactions/<txid:re:[a-f0-9]+>/prime_input', method='GET', callback=self.get_prime_input_address)
        self.route('/spellbook/transactions/<txid:re:[a-f0-9]+>', method='GET', callback=self.get_transaction)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/transactions', method='GET', callback=self.get_transactions)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/balance', method='GET', callback=self.get_balance)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/utxos', method='GET', callback=self.get_utxos)

        # Routes for Simplified Inputs List (SIL)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/SIL', method='GET', callback=self.get_sil)

        # Routes for Profile
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/profile', method='GET', callback=self.get_profile)

        # Routes for Simplified UTXO List (SUL)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/SUL', method='GET', callback=self.get_sul)

        # Routes for Linked Lists
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/LAL', method='GET', callback=self.get_lal)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/LBL', method='GET', callback=self.get_lbl)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/LRL', method='GET', callback=self.get_lrl)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/LSL', method='GET', callback=self.get_lsl)

        # Routes for Random Address
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/random/SIL', method='GET', callback=self.get_random_address_from_sil)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/random/LBL', method='GET', callback=self.get_random_address_from_lbl)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/random/LRL', method='GET', callback=self.get_random_address_from_lrl)
        self.route('/spellbook/addresses/<address:re:[a-zA-Z1-9]+>/random/LSL', method='GET', callback=self.get_random_address_from_lsl)

        # Routes for Triggers
        self.route('/spellbook/triggers', method='GET', callback=self.get_triggers)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.get_trigger)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='POST', callback=self.save_trigger)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='DELETE', callback=self.delete_trigger)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/activate', method='GET', callback=self.activate_trigger)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/message', method='POST', callback=self.verify_signed_message)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/get', method='GET', callback=self.http_get_request)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/post', method='POST', callback=self.http_post_request)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/delete', method='DELETE', callback=self.http_delete_request)
        self.route('/spellbook/triggers/<trigger_id:re:[a-zA-Z0-9_\-.]+>/check', method='GET', callback=self.check_trigger)
        self.route('/spellbook/check_triggers', method='GET', callback=self.check_all_triggers)

        # Additional routes for Rest API endpoints
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.http_get_request)
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='OPTIONS', callback=self.http_options_request)
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='POST', callback=self.http_post_request)
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='DELETE', callback=self.http_delete_request)
        self.route('/html/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.html_request)
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>/message', method='POST', callback=self.verify_signed_message)
        self.route('/api/<trigger_id:re:[a-zA-Z0-9_\-.]+>/message', method='OPTIONS', callback=self.http_options_request)

        self.route('/api/sign_message', method='POST', callback=self.sign_message)

        # Routes for file downloads
        self.route('/files/<trigger_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.file_download)

        # Routes for QR image generation
        self.route('/api/qr', method='GET', callback=self.qr)

        # Routes for Actions
        self.route('/spellbook/actions', method='GET', callback=self.get_actions)
        self.route('/spellbook/actions/<action_id:re:[a-zA-Z0-9_\-.]+>', method='GET', callback=self.get_action)
        self.route('/spellbook/actions/<action_id:re:[a-zA-Z0-9_\-.]+>', method='POST', callback=self.save_action)
        self.route('/spellbook/actions/<action_id:re:[a-zA-Z0-9_\-.]+>', method='DELETE', callback=self.delete_action)
        self.route('/spellbook/actions/<action_id:re:[a-zA-Z0-9_\-.]+>/run', method='GET', callback=self.run_action)

        # Routes for retrieving log messages
        self.route('/spellbook/logs/<filter_string>', method='GET', callback=self.get_logs)

        # Routes for RevealSecret actions
        self.route('/spellbook/actions/<action_id:re:[a-zA-Z0-9_\-.]+>/reveal', method='GET', callback=self.get_reveal)

        # Routes for uploading files
        self.route('/spellbook/upload', method='POST', callback=self.upload_file)
        self.route('/spellbook/upload', method='OPTIONS', callback=self.upload_file)
        self.route('/spellbook/transcribe', method='POST', callback=self.transcribe)
        self.route('/spellbook/transcribe', method='OPTIONS', callback=self.transcribe)

        # Check if there are explorers configured, this will also initialize the default explorers on first startup
        if len(get_explorers()) == 0:
            LOG.warning('No block explorers configured!')

        try:
            # start the webserver for the REST API
            if get_enable_ssl() is True:
                self.run(host=self.host, port=self.port, debug=False, server='sslwebserver')
            else:
                self.run(host=self.host, port=self.port, debug=True, server='cheroot')

        except Exception as ex:
            LOG.error('An exception occurred in the main loop: %s' % ex)
            error_traceback = traceback.format_exc()
            for line in error_traceback.split('\n'):
                LOG.error(line)

            if get_mail_on_exception() is True:
                variables = {'HOST': get_host(),
                             'TRACEBACK': error_traceback}
                body_template = os.path.join('server_exception')
                sendmail(recipients=get_notification_email(),
                         subject='Main loop Exception occurred @ %s' % get_host(),
                         body_template=body_template,
                         variables=variables)

    def index(self):
        return

    @staticmethod
    def get_favicon():
        return static_file('favicon.ico', root='.')

    @staticmethod
    def initialize_requests_log(logs_dir):
        # Create a log file for the http requests to the REST API
        logger = logging.getLogger('api_requests')

        file_handler = RotatingFileHandler(os.path.join(logs_dir, 'requests.txt'), maxBytes=10000000, backupCount=5)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(file_handler)

        logger.setLevel(logging.DEBUG)

        return logger

    def log_to_logger(self, fn):
        @wraps(fn)
        def _log_to_logger(*args, **kwargs):
            start_time = int(round(time.time() * 1000))
            request_time = datetime.now()

            # Log information about the request before it is processed for debugging purposes
            REQUESTS_LOG.info('%s | %s | %s | %s' % (request_time,
                                                     request.remote_addr,
                                                     request.method,
                                                     request.url))

            if request.headers is not None:
                for key, value in request.headers.items():
                    REQUESTS_LOG.info('  HEADERS | %s: %s' % (key, str(value).encode('utf-8')))

            if request.json is not None:
                for key, value in request.json.items():
                    REQUESTS_LOG.info('  BODY | %s: %s' % (key, str(value).encode('utf-8')))

            actual_response = response
            try:
                actual_response = fn(*args, **kwargs)
            except Exception as ex:
                response_status = '500 ' + str(ex)
                LOG.error('%s caused an exception: %s' % (request.url, ex))
                error_traceback = traceback.format_exc()
                for line in error_traceback.split('\n'):
                    LOG.error(line)

                if get_mail_on_exception() is True:
                    variables = {'HOST': get_host(),
                                 'TRACEBACK': error_traceback}
                    body_template = os.path.join('server_exception')
                    sendmail(recipients=get_notification_email(),
                             subject='Exception occurred @ %s' % get_host(),
                             body_template=body_template,
                             variables=variables)

            else:
                response_status = response.status

            end_time = int(round(time.time() * 1000))
            REQUESTS_LOG.info('%s | %s | %s | %s | %s | %s ms' % (request_time,
                                                                  request.remote_addr,
                                                                  request.method,
                                                                  request.url,
                                                                  response_status,
                                                                  end_time - start_time))
            return actual_response

        return _log_to_logger

    @staticmethod
    @output_json
    def ping():
        LOG.info('Pong')
        response.content_type = 'application/json'
        return {'success': True}

    @staticmethod
    @enable_cors
    @output_json
    def get_llms():
        response.content_type = 'application/json'
        llms = load_llms()
        if llms is not None:
            return [k for k, v in llms.items()]
        else:
            return {'error': 'Unable to retrieve LLMs'}

    @staticmethod
    @enable_cors
    @output_json
    def get_llm_config(llm_id):
        response.content_type = 'application/json'
        llm_config = get_llm_config(llm_id)

        # Mask sensitive information like API keys for security
        if 'api_key' in llm_config and llm_config['api_key'] not in ["", None]:
            llm_config['api_key'] = '********'

        if llm_config is not None:
            return llm_config
        else:
            return {'error': 'No LLM configured with id: %s' % llm_id}

    @staticmethod
    @enable_cors
    @output_json
    @authentication_required
    def save_llm_config(llm_id):
        save_llm_config(llm_id, request.json)

    @staticmethod
    @output_json
    @authentication_required
    def delete_llm(llm_id):
        delete_llm(llm_id)

    @staticmethod
    @output_json
    def get_explorers():
        response.content_type = 'application/json'
        explorers = get_explorers()
        if explorers is not None:
            return explorers
        else:
            return {'error': 'Unable to retrieve explorer_ids'}

    @staticmethod
    @authentication_required
    def save_explorer(explorer_id):
        save_explorer(explorer_id, request.json)

    @staticmethod
    @output_json
    @authentication_required
    def get_explorer_config(explorer_id):
        response.content_type = 'application/json'
        explorer_config = get_explorer_config(explorer_id)
        if explorer_config is not None:
            return explorer_config
        else:
            return {'error': 'No explorer configured with id: %s' % explorer_id}

    @staticmethod
    @authentication_required
    def delete_explorer(explorer_id):
        delete_explorer(explorer_id)

    @staticmethod
    @output_json
    @use_explorer
    def get_latest_block():
        response.content_type = 'application/json'
        return latest_block()

    @staticmethod
    @output_json
    @use_explorer
    def get_block_by_height(height):
        response.content_type = 'application/json'
        return block_by_height(height)

    @staticmethod
    @output_json
    @use_explorer
    def get_block_by_hash(block_hash):
        response.content_type = 'application/json'
        return block_by_hash(block_hash)

    @staticmethod
    @output_json
    @use_explorer
    def get_prime_input_address(txid):
        response.content_type = 'application/json'
        return prime_input_address(txid)

    @staticmethod
    @output_json
    @use_explorer
    def get_transaction(txid):
        response.content_type = 'application/json'
        return transaction(txid)

    @staticmethod
    @output_json
    @use_explorer
    def get_transactions(address):
        response.content_type = 'application/json'
        return transactions(address)

    @staticmethod
    @output_json
    @use_explorer
    def get_balance(address):
        response.content_type = 'application/json'
        return balance(address)

    @staticmethod
    @output_json
    @use_explorer
    def get_utxos(address):
        response.content_type = 'application/json'
        return utxos(address, int(request.query.confirmations))

    @staticmethod
    @output_json
    @use_explorer
    def get_sil(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        return get_sil(address, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_profile(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        return get_profile(address, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_sul(address):
        response.content_type = 'application/json'
        confirmations = int(request.json['confirmations'])
        return get_sul(address, confirmations)

    @staticmethod
    @output_json
    @use_explorer
    def get_lal(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lal(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lbl(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lbl(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lrl(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lrl(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_lsl(address):
        response.content_type = 'application/json'
        block_height = int(request.json['block_height'])
        xpub = request.json['xpub']
        return get_lsl(address, xpub, block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_random_address_from_sil(address):
        response.content_type = 'application/json'
        rng_block_height = int(request.json['rng_block_height'])
        sil_block_height = int(request.json['sil_block_height'])
        return random_address_from_sil(address=address, sil_block_height=sil_block_height, rng_block_height=rng_block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_random_address_from_lbl(address):
        response.content_type = 'application/json'
        rng_block_height = int(request.json['rng_block_height'])
        sil_block_height = int(request.json['sil_block_height'])
        xpub = request.json['xpub']
        return random_address_from_lbl(address=address, xpub=xpub, sil_block_height=sil_block_height, rng_block_height=rng_block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_random_address_from_lrl(address):
        response.content_type = 'application/json'
        rng_block_height = int(request.json['rng_block_height'])
        sil_block_height = int(request.json['sil_block_height'])
        xpub = request.json['xpub']
        return random_address_from_lrl(address=address, xpub=xpub, sil_block_height=sil_block_height, rng_block_height=rng_block_height)

    @staticmethod
    @output_json
    @use_explorer
    def get_random_address_from_lsl(address):
        response.content_type = 'application/json'
        rng_block_height = int(request.json['rng_block_height'])
        sil_block_height = int(request.json['sil_block_height'])
        xpub = request.json['xpub']
        return random_address_from_lsl(address=address, xpub=xpub, sil_block_height=sil_block_height, rng_block_height=rng_block_height)

    @staticmethod
    @output_json
    def get_triggers():
        response.content_type = 'application/json'
        triggers = get_triggers()
        if triggers is not None:
            return triggers
        else:
            return {'error': 'Unable to retrieve explorer_ids'}

    @staticmethod
    @output_json
    @authentication_required
    def get_trigger(trigger_id):
        response.content_type = 'application/json'
        trigger_config = get_trigger_config(trigger_id)
        if trigger_config is not None:
            return trigger_config
        else:
            return {'error': 'No trigger configured with id: %s' % trigger_id}

    @staticmethod
    @output_json
    @authentication_required
    def save_trigger(trigger_id):
        response.content_type = 'application/json'
        return save_trigger(trigger_id, **request.json)

    @staticmethod
    @output_json
    @authentication_required
    def delete_trigger(trigger_id):
        response.content_type = 'application/json'
        return delete_trigger(trigger_id)

    @staticmethod
    @output_json
    @authentication_required
    def activate_trigger(trigger_id):
        response.content_type = 'application/json'
        return activate_trigger(trigger_id)

    @staticmethod
    @enable_cors
    @output_json
    def verify_signed_message(trigger_id):
        response.content_type = 'application/json'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return verify_signed_message(trigger_id, **data)

    @staticmethod
    @output_json
    @authentication_required
    def sign_message():
        LOG.info('Sign message request received')
        LOG.info(f'request json: {request.json}')
        response.content_type = 'application/json'
        return sign_message(**request.json)

    @staticmethod
    @enable_cors
    @output_json
    def http_options_request(trigger_id):
        response.content_type = 'application/json'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return http_options_request(trigger_id, **data)

    @staticmethod
    @enable_cors
    @output_json
    def http_get_request(trigger_id):
        response.content_type = 'application/json'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return http_get_request(trigger_id, **data)

    @staticmethod
    @enable_cors
    @output_json
    def http_post_request(trigger_id):
        response.content_type = 'application/json'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return http_post_request(trigger_id, **data)

    @staticmethod
    @output_json
    def http_delete_request(trigger_id):
        response.content_type = 'application/json'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return http_delete_request(trigger_id, **data)

    @staticmethod
    def html_request(trigger_id):
        response.content_type = 'text/html'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return http_get_request(trigger_id, **data)

    @staticmethod
    def qr():
        response.content_type = 'image/png'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return generate_qr(**data)

    @staticmethod
    @output_json
    @use_explorer
    @authentication_required
    def check_trigger(trigger_id):
        response.content_type = 'application/json'
        return check_triggers(trigger_id)

    @staticmethod
    @output_json
    @use_explorer
    @authentication_required
    def check_all_triggers():
        response.content_type = 'application/json'
        return check_triggers()

    @staticmethod
    @output_json
    def get_actions():
        response.content_type = 'application/json'
        actions = get_actions()
        if actions is not None:
            return actions
        else:
            return {'error': 'Unable to retrieve action_ids'}

    @staticmethod
    @output_json
    @authentication_required
    def get_action(action_id):
        response.content_type = 'application/json'
        action_config = get_action_config(action_id)
        if action_config is not None:
            return action_config
        else:
            return {'error': 'No action with id %s found' % action_id}

    @staticmethod
    @output_json
    @authentication_required
    def save_action(action_id):
        response.content_type = 'application/json'
        return save_action(action_id, **request.json)

    @staticmethod
    @output_json
    @authentication_required
    def delete_action(action_id):
        response.content_type = 'application/json'
        return delete_action(action_id)

    @staticmethod
    @output_json
    @authentication_required
    def run_action(action_id):
        response.content_type = 'application/json'
        return run_action(action_id)

    @staticmethod
    @output_json
    def get_reveal(action_id):
        response.content_type = 'application/json'
        return get_reveal(action_id)

    @staticmethod
    @output_json
    @authentication_required
    def get_logs(filter_string):
        response.content_type = 'application/json'
        return get_logs(filter_string=filter_string)

    @staticmethod
    @enable_cors
    def file_download(trigger_id):
        response.content_type = 'image/png'
        data = request.json if request.json is not None else {}

        # Also add parameters passed via the query string to the data, if any parameters have the same name then the query string has priority
        query = dict(request.query)
        data.update(query)

        return file_download(trigger_id, **data)

    @staticmethod
    @enable_cors
    def upload_file():
        if get_enable_uploads() is False:
            LOG.error("File uploads are not enabled")
            response.status = 403
            return {"error": "File uploads are not enabled"}

        uploads_dir = get_uploads_dir()
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        uploaded_file = request.files.get('file')

        if not uploaded_file:
            LOG.error("No file uploaded")
            response.status = 400
            return {"error": "No file uploaded"}

        allowed_extensions = get_allowed_extensions().split(',')
        file_extension = os.path.splitext(uploaded_file.filename)[1]

        if file_extension[1:] not in allowed_extensions:
            LOG.error(f"File extension {file_extension} is not allowed")
            response.status = 403
            return {"error": f"File extension {file_extension} is not allowed"}

        # Read file content into a variable
        file_content = uploaded_file.file.read()

        # Validate file type with python-magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_content)
        LOG.info(f'Uploaded file type: {file_type}')
        if file_type.split('/')[1] not in allowed_extensions:
            LOG.error(f"File type {file_type} is not allowed")
            response.status = 403
            return {"error": f"File type {file_type} is not allowed"}

        max_file_size = get_max_file_size()
        if len(file_content) > max_file_size:
            LOG.error(f"File size exceeds maximum allowed size of {max_file_size} bytes, file size is {len(file_content)} bytes")
            response.status = 413
            return {"error": f"File size exceeds maximum allowed size of {max_file_size} bytes, file size is {len(file_content)} bytes"}

        # Reset the file pointer to the beginning
        uploaded_file.file.seek(0)

        unique_id = str(uuid.uuid4())
        file_path = os.path.join(uploads_dir, f"{unique_id}{file_extension}")

        try:
            uploaded_file.save(file_path)
            return {"file_id": f"{unique_id}{file_extension}", "file_name": uploaded_file.filename}

        except Exception as e:
            response.status = 500
            return {"error": str(e)}

    @staticmethod
    @enable_cors
    def transcribe():
        start = time.time()
        if get_enable_transcribe() is False:
            return HTTPResponse(status=403, body={"error": "Transcribe endpoint is not enabled"})

        uploaded_file = request.files.get('file')

        if not uploaded_file:
            return HTTPResponse(status=400, body={"error": "No file uploaded"})

        allowed_extensions = get_allowed_extensions_transcribe().split(',')
        file_extension = os.path.splitext(uploaded_file.filename)[1]

        if file_extension[1:] not in allowed_extensions:
            return HTTPResponse(status=403, body={"error": f"File extension {file_extension} is not allowed"})

        # Read file content into a variable
        file_content = uploaded_file.file.read()

        # Validate file type with python-magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file_content)
        LOG.info(f'Transcribing audio, detected file type: {file_type}')
        if file_type not in ['audio/mpeg', 'video/webm', 'video/mp4', 'audio/ogg']:
            return HTTPResponse(status=403, body={"error": f"File type {file_type} is not allowed"})

        if file_type == 'video/mp4':
            # Audio file comes from FlutterFlow, which uses a different codec that is incompatible, convert to opus
            # save the uploaded file to disk, remove the old files if they exists
            if os.path.exists('tmp_audio.mp3'):
                os.remove('tmp_audio.mp3')

            if os.path.exists('opus_audio.opus'):
                os.remove('opus_audio.opus')

            # Reset the file pointer to the beginning
            uploaded_file.file.seek(0)
            uploaded_file.save('tmp_audio.mp3')
            LOG.info(f"Saved temporary file to disk: tmp_audio.mp3")

            convert_aac_to_opus('tmp_audio.mp3', 'opus_audio.opus')

            # replace uploaded file with the opus file
            uploaded_file.filename = 'opus_audio.opus'
            uploaded_file.file = open('opus_audio.opus', 'rb')


        max_file_size = get_max_file_size_transcribe()
        if len(file_content) > max_file_size:
            return HTTPResponse(status=413, body={"error": f"File size exceeds maximum allowed size of {max_file_size} bytes, file size is {len(file_content)} bytes"})

        # Reset the file pointer to the beginning
        uploaded_file.file.seek(0)

        LOG.info("Transcribing audio file")
        segments, info = WHISPER_MODEL.transcribe(uploaded_file.file, beam_size=5, language="en", max_new_tokens=128, condition_on_previous_text=False)
        uploaded_file.file.close()

        transcription = {'segments': []}
        full_text = ""
        for segment in segments:
            transcription['segments'].append({"start": segment.start, "end": segment.end, "text": segment.text})
            full_text += segment.text + " "

        transcription['full_text'] = full_text.rstrip().lstrip()
        LOG.info(transcription['full_text'])

        end = time.time()
        transcription['calculation_time'] = end - start
        return transcription

def convert_aac_to_opus(input_file, opus_file):
    command = f"ffmpeg -i {input_file} -c:a libopus {opus_file}"
    subprocess.run(command, shell=True)
    # Ensure the file is closed after it's used
    with open(opus_file, 'rb') as file:
        pass


if __name__ == "__main__":
    # Check if the IP address in the configuration file is set, if not then set it
    configuration_file = os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf')
    config = ConfigParser()
    config.read(os.path.join(PROGRAM_DIR, 'configuration', 'spellbook.conf'))
    if config.get(section='RESTAPI', option='host') == '':
        my_ip = what_is_my_ip()
        config.set(section='RESTAPI', option='host', value=my_ip)
        with open(configuration_file, 'w') as output_file:
            config.write(output_file)
            LOG.info(f'spellbook.conf file updated with host IP address: {my_ip}')

    # Create main parser
    parser = argparse.ArgumentParser(description='Bitcoin spellbookServer command line interface', formatter_class=argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('-s', '--ssl', help='Run spellbook server with SSL', action='store_true')

    # Parse the command line arguments
    args = parser.parse_args()

    SpellbookRESTAPI()
