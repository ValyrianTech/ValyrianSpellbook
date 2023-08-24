import configparser
import os

# Define the configuration parameters
config_params = {
    "RESTAPI": {
        "host": "<host>",
        "port": "<port>",
        "notification_email": "<notification_email>",
        "mail_on_exception": "<mail_on_exception>",
        "python_exe": "<python_exe>"
    },
    "Authentication": {
        "key": "<key>",
        "secret": "<secret>"
    },
    "SMTP": {
        "enable_smtp": "<enable_smtp>",
        "from_address": "<from_address>",
        "host": "<smtp_host>",
        "port": "<smtp_port>",
        "user": "<user>",
        "password": "<password>"
    },
    "Wallet": {
        "enable_wallet": "<enable_wallet>",
        "wallet_dir": "<wallet_dir>",
        "default_wallet": "<default_wallet>",
        "use_testnet": "<use_testnet>"
    },
    "Transactions": {
        "minimum_output_value": "<minimum_output_value>",
        "max_tx_fee_percentage": "<max_tx_fee_percentage>"
    },
    "IPFS": {
        "enable_ipfs": "<enable_ipfs>",
        "api_host": "<api_host>",
        "api_port": "<api_port>",
        "gateway_host": "<gateway_host>",
        "gateway_port": "<gateway_port>"
    },
    "APPS": {
        "app_data_dir": "<app_data_dir>"
    },
    "SSL": {
        "enable_ssl": "<enable_ssl>",
        "domain_name": "<domain_name>",
        "certificate": "<certificate>",
        "private_key": "<private_key>",
        "certificate_chain": "<certificate_chain>"
    },
    "Twitter": {
        "enable_twitter": "<enable_twitter>",
        "consumer_key": "<consumer_key>",
        "consumer_secret": "<consumer_secret>",
        "access_token": "<access_token>",
        "access_token_secret": "<access_token_secret>",
        "bearer_token": "<bearer_token>"
    },
    "OpenAI": {
        "enable_openai": "<enable_openai>",
        "api_key": "<api_key>",
        "organization": "<organization>"
    },
    "Mastodon": {
        "enable_mastodon": "<enable_mastodon>",
        "client_id": "<client_id>",
        "client_secret": "<client_secret>",
        "access_token": "<access_token>",
        "api_base_url": "<api_base_url>"
    },
    "Nostr": {
        "enable_nostr": "<enable_nostr>",
        "nsec": "<nsec>"
    },
    "Oobabooga": {
        "enable_oobabooga": "<enable_oobabooga>",
        "host": "<oobabooga_host>",
        "port": "<oobabooga_port>"
    }
}

# Load the configuration file
config = configparser.ConfigParser()
config.read('/spellbook/configuration/spellbook.conf')

# Replace the placeholders with the actual values
for section in config.sections():
    for key in config[section]:
        env_var_name = (section + '_' + key).upper()
        env_var_value = os.environ.get(env_var_name)
        if env_var_value is not None:
            config.set(section, key, env_var_value)

# Write the updated configuration back to the file
with open('/spellbook/configuration/spellbook.conf', 'w') as configfile:
    config.write(configfile)
