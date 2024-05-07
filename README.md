# Valyrian Spellbook

The Valyrian Spellbook, formerly known as the Bitcoin Spellbook, is an open platform provided by Valyrian Tech, designed to simplify the creation and management of Bitcoin-related applications and integrations with Large Language Models (LLMs). It is aimed at speeding up development, enhancing automation, and enabling even those with minimal coding experience to deploy sophisticated applications in the cryptocurrency realm.

## Table of Contents

- [Features](#features)
  - [Bitcoin Blockchain Features](#bitcoin-blockchain-features)
  - [Large Language Model (LLM) Features](#large-language-model-llm-features)
  - [Actions and Triggers System](#actions-and-triggers-system)
- [Installation](#installation)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Using the CLI](#using-the-cli)
- [Triggers](#triggers)
- [Actions](#actions)
- [Scripts](#scripts)
- [Example Apps](#example-apps)
- [Additional Tools](#additional-tools)
- [Donations and Social Media](#donations-and-social-media)

---

## Features

### Bitcoin Blockchain Features

- **Transaction Management**: Send and receive Bitcoin transactions.
- **Data Extraction**: Fetch and analyze data from the blockchain.
- **Explorer Management**: Add, configure, and manage blockchain explorers.

### Large Language Model (LLM) Features

- **Integration of Multiple Models**: Manage various LLMs through dynamic API end points.
- **Text Processing and Interaction**: Automate responses and generate text.

### Actions and Triggers System

- **Automated Workflow**: Setup triggers that automatically invoke actions based on specific conditions.
- **Extensibility**: Easily extendible with custom scripts and integrations to fit any use case.

---

## Installation

Run the following commands to set up the Valyrian Spellbook:
The install script will install the required dependencies and set up the configuration files.

```bash
cd /
wget https://raw.githubusercontent.com/ValyrianTech/ValyrianSpellbook/master/install-spellbook.sh
sh install-spellbook.sh
```
Refer to the provided `configuration/` directory to adjust settings for your environment.

---

## Usage

### Starting the Server

```bash
python spellbookserver.py
```

### Using the CLI

The CLI tool `spellbook.py` helps manage triggers, actions, and configurations:

```bash
spellbook.py -h
```

---

## Triggers

Triggers invoke actions based on specific conditions:

- **Balance**: Activates if the balance of a specified address is above a certain threshold.
- **Received/Sent**: Monitors received or sent amounts for a given address.
- **Block Height**: Triggers once the blockchain reaches a specified height.
- **Timestamp and Recurring**: Schedule triggers based on time.
- **HTTP Requests**: Activates upon HTTP GET, POST, or DELETE requests.
- **Manual Activation**: Trigger manually via a specific API endpoint.
- **Dead Man's Switch**: A time-based trigger that sends notifications if not reset periodically.

---

## Actions

Actions perform tasks when triggered. Here are a few example actions:

- **Send Transaction**: Automates Bitcoin transactions.
- **Send Email**: Configures and sends emails automatically.
- **Command and SpawnProcess**: Executes system commands or spawns new processes.
- **Reveal Secret**: Reveals a pre-configured secret upon trigger activation.
- **Webhook**: Sends data to specified webhooks.

---

## Scripts

Custom Python scripts can be added and managed, providing tailor-made functionalities enacted by triggers:

```python
# Template script
from spellbookscripts.spellbookscript import SpellbookScript

class CustomScript(SpellbookScript):
    def run(self):
        # Your code here
```

---

## Example Apps

Comprehensive scenarios showcasing what the Valyrian Spellbook can achieve:

- **Payment Processor**: Automates handling of Bitcoin transactions.
- **Notary Service**: Utilizes blockchain for timestamping documents.
- **Lottery System**: A Bitcoin-based lottery implementation.
- Take a look at the `apps/` directory for more.

---

## Additional Tools

- **bitcoinwand.py**: Sign messages or verify signatures using Bitcoin keys.
- **transaction_listener.py**: Listens to transaction broadcasts relevant to watched addresses.
- **hot_wallet.py**: Manages and secures private keys.

---


Blockexplorers
--------------
The default configuration will use Blockchain.info and BTC.com as explorers.  
It is recommended to keep the default explorers configuration, but if you want to change this:  

Use the **spellbook.py** CLI  to add the blockexplorers you want to use.  

You can add multiple blockexplorers and set a priority for each one, if the first one is offline, the next one will be used.  
example: **spellbook.py save_explorer blockchain.info Blockchain.info 1**  

Run **spellbook.py save_explorer -h** for more information  

Currently supported blockchain explorers are:  
* Blockchain.info  
* BTC.com    
* Any Insight blockexplorer (blockexplorer.com) 
* Blocktrail.com (testnet seems to be broken, no longer maintained)  
* Chain.so (not recommended)


Segwit
------
There currently is partial segwit support. It is possible to send to segwit addresses (including bech32 addresses).

What is not possible yet:  
* sending from segwit addresses (I'm working on it)  
* looking up transactions or balances from bech32 addresses (this is because blockchain.info and BTC.com do not support this yet)


## Donations and Social Media
If you find this project useful, consider making a donation to support development:
[1Woutere8RCF82AgbPCc5F4KuYVvS4meW](https://www.blocktrail.com/BTC/address/1Woutere8RCF82AgbPCc5F4KuYVvS4meW)

Visit [www.valyrian.tech](http://www.valyrian.tech "Valyrian Tech") to keep up with the latest developments!

[Twitter: @WouterGlorieux](https://twitter.com/WouterGlorieux)

[LinkedIn](https://www.linkedin.com/in/wouterglorieux)

