#!/bin/bash

# run this script on a fresh linux machine to install the Bitcoin Spellbook and all requirements
# Before running this script, create a new user named spellbook with sudo rights and run this script as that user from the home directory.
#
# sudo adduser spellbook
# usermod -aG sudo spellbook
# su spellbook
# cd ~
# wget https://raw.githubusercontent.com/ValyrianTech/BitcoinSpellbook-v0.3/master/install-spellbook.sh
# sh install-spellbook.h

cd ~
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install git python2.7 python-dev python-pip -y

mkdir spellbook_wallet
mkdir spellbook_data

git clone https://github.com/ValyrianTech/BitcoinSpellbook-v0.3.git spellbook
cd spellbook

pip install -r requirements.txt

./quickstart.py
