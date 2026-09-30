# Vulture whitelist. Every identifier referenced below is treated as "used"
# by vulture. Framework hooks (decorator-registered routes), dynamic plugin
# APIs, and pytest-mock injected fixtures are not visible to static analysis.
# One identifier per line; attributes use the "_.name" form.

# FastAPI / Bottle route handlers (registered via decorators).
not_found_handler
server_error_handler
list_actions
new_action
view_action
edit_action
blockchain_index
view_block
view_transaction
view_address
login_page
logout
list_explorers
new_explorer
view_explorer
edit_explorer
list_llms
new_llm
view_llm
save_llm
list_triggers
new_trigger
view_trigger
edit_trigger

# Dynamic-plugin / public-API classes.
Lottery
Notary
RedeemVoucher

# Config constants, protocol and framework attributes.
FEE_TYPE
serialized
exc_type
exc_val
exc_tb
get_llms_parser
get_explorers_parser
base64_regex
THINKING_LEVELS
DATABASE
_.binc
_.MEMFILE_MAX
_.ssl_adapter

# Integration-test module constants.
testnet_P2WPKH
testnet_P2WSH

# Dunder / unittest protocol attributes and functions.
_.__enter__
_.__exit__
_.__aiter__
_.__iter__
_.stop_generation
_.testscript
setUpModule
tearDownModule
_passthrough_output_json

# Test helpers and injected mock arguments.
kw
fn_name
module
reset_globals
address_compressed
address_uncompressed
public_key_compressed
public_key_uncompressed
mock_amt
mock_api_key
mock_app_dir
mock_auth
mock_available
mock_bearer
mock_bitcoin_msg
mock_bottle_request
mock_bottle_response
mock_cert
mock_channel
mock_consumer_key
mock_consumer_secret
mock_cpu
mock_domain
mock_dotenv
mock_dumps
mock_email
mock_enable
mock_ensure
mock_exists
mock_explorers
mock_ext
mock_filters
mock_find
mock_find_single
mock_format
mock_from
mock_get_actions
mock_get_config
mock_get_default
mock_getenv
mock_get_host
mock_get_nsec
mock_get_token
mock_get_wallet
mock_host
mock_id
mock_ip
mock_ipfs_api
mock_last
mock_loads
mock_login
mock_logout
mock_low_fee
mock_make_tx
mock_max
mock_max_fee
mock_med_fee
mock_parent_activate
mock_parser_cls
mock_pass
mock_phase
mock_platform
mock_port
mock_print
mock_python
mock_ram
mock_router
mock_sender
mock_ssl
mock_ssl_enabled
mock_stdout
mock_stop
mock_system
mock_testnet
mock_time
mock_token
mock_transcribe
mock_ts
mock_txhash
mock_txid
mock_url
mock_user
mock_valid
mock_validate
