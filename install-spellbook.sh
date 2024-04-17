#!/bin/bash

# run this script on a fresh linux machine to install the Valyrian Spellbook and all requirements
# this script will install The Valyrian Spellbook as root and create all directories at the root of the system

# cd /
# wget https://raw.githubusercontent.com/ValyrianTech/ValyrianSpellbook/master/install-spellbook.sh
# sh install-spellbook.sh

cd /
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install git python3.10 python3.10-dev python3-pip -y
sudo apt-get install libssl-dev
sudo apt-get install ffmpeg -y

mkdir spellbook_wallet
mkdir spellbook_data

git clone https://github.com/ValyrianTech/ValyrianSpellbook.git spellbook
cd /spellbook

python3.10 -m pip install -r requirements.txt

# add the spellbook to the pythonpath so it can correctly import modules
export PYTHONPATH=$PYTHONPATH:/spellbook

python3.10 ./quickstart.py
