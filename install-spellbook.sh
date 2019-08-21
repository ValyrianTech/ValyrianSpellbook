#!/bin/bash

# run this script on a fresh linux machine to install the Bitcoin Spellbook and all requirements
# this script will install The Bitcoin Spellbook as root and create all directories at the root of the system

# cd /
# wget https://raw.githubusercontent.com/ValyrianTech/BitcoinSpellbook/master/install-spellbook.sh
# sh install-spellbook.sh

cd /
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install git python3.7 python-dev python-pip -y

mkdir spellbook_wallet
mkdir spellbook_data

git clone https://github.com/ValyrianTech/BitcoinSpellbook.git spellbook
cd /spellbook

pip install -r requirements.txt

# add the spellbook to the pythonpath so it can correctly import modules
export PYTHONPATH=$PYTHONPATH:/spellbook

./quickstart.py
