# Use an official Python runtime as a parent image
FROM ubuntu:22.04

# Set the working directory in the container to /
WORKDIR /

# Update and upgrade the system
RUN apt-get update -y && apt-get upgrade -y

# Install any needed packages specified in requirements.txt
RUN apt-get install git python3.10 python3.10-dev python3-pip libssl-dev -y

# Clone the Valyrian Spellbook repository
RUN git clone https://github.com/ValyrianTech/ValyrianSpellbook.git spellbook

# Rename the example configuration file to spellbook.conf
RUN mv /spellbook/configuration/example_configuration_file.conf /spellbook/configuration/spellbook.conf

# Define environment variables for the configuration parameters
ENV RESTAPI_HOST=<host>
ENV RESTAPI_PORT=<port>
ENV RESTAPI_NOTIFICATION_EMAIL=<notification_email>
ENV RESTAPI_MAIL_ON_EXCEPTION=<mail_on_exception>
ENV RESTAPI_PYTHON_EXE=<python_exe>
ENV AUTHENTICATION_KEY=<key>
ENV AUTHENTICATION_SECRET=<secret>
ENV SMTP_ENABLE_SMTP=<enable_smtp>
ENV SMTP_FROM_ADDRESS=<from_address>
ENV SMTP_HOST=<smtp_host>
ENV SMTP_PORT=<smtp_port>
ENV SMTP_USER=<user>
ENV SMTP_PASSWORD=<password>
ENV WALLET_ENABLE_WALLET=<enable_wallet>
ENV WALLET_WALLET_DIR=<wallet_dir>
ENV WALLET_DEFAULT_WALLET=<default_wallet>
ENV WALLET_USE_TESTNET=<use_testnet>
ENV TRANSACTIONS_MINIMUM_OUTPUT_VALUE=<minimum_output_value>
ENV TRANSACTIONS_MAX_TX_FEE_PERCENTAGE=<max_tx_fee_percentage>
ENV IPFS_ENABLE_IPFS=<enable_ipfs>
ENV IPFS_API_HOST=<api_host>
ENV IPFS_API_PORT=<api_port>
ENV IPFS_GATEWAY_HOST=<gateway_host>
ENV IPFS_GATEWAY_PORT=<gateway_port>
ENV APPS_APP_DATA_DIR=<app_data_dir>
ENV SSL_ENABLE_SSL=<enable_ssl>
ENV SSL_DOMAIN_NAME=<domain_name>
ENV SSL_CERTIFICATE=<certificate>
ENV SSL_PRIVATE_KEY=<private_key>
ENV SSL_CERTIFICATE_CHAIN=<certificate_chain>
ENV TWITTER_ENABLE_TWITTER=<enable_twitter>
ENV TWITTER_CONSUMER_KEY=<consumer_key>
ENV TWITTER_CONSUMER_SECRET=<consumer_secret>
ENV TWITTER_ACCESS_TOKEN=<access_token>
ENV TWITTER_ACCESS_TOKEN_SECRET=<access_token_secret>
ENV TWITTER_BEARER_TOKEN=<bearer_token>
ENV OPENAI_ENABLE_OPENAI=<enable_openai>
ENV OPENAI_API_KEY=<api_key>
ENV OPENAI_ORGANIZATION=<organization>
ENV MASTODON_ENABLE_MASTODON=<enable_mastodon>
ENV MASTODON_CLIENT_ID=<client_id>
ENV MASTODON_CLIENT_SECRET=<client_secret>
ENV MASTODON_ACCESS_TOKEN=<access_token>
ENV MASTODON_API_BASE_URL=<api_base_url>
ENV NOSTR_ENABLE_NOSTR=<enable_nostr>
ENV NOSTR_NSEC=<nsec>

# Run the Python script to replace the placeholders in the configuration file
COPY replace_placeholders.py /replace_placeholders.py
RUN python3.10 /replace_placeholders.py

# Install Python dependencies
RUN python3.10 -m pip install -r /spellbook/requirements.txt

# Make port 42069 available to the world outside this container
EXPOSE 42069

# Define environment variable
ENV NAME ValyrianSpellbook

# Copy the startup script into the container
COPY start.sh /start.sh

# Run start.sh when the container launches
CMD ["/bin/bash", "/start.sh"]
