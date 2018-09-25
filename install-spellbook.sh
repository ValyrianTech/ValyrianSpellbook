#!/bin/bash
cd ~
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git python2.7 python-dev
mkdir spellbook
cd spellbook
mkdir wallet
mkdir app_data
git init
git clone https://github.com/ValyrianTech/BitcoinSpellbook-v0.3.git spellbook
cd spellbook
python install pip
pip install pipreqs
pipreqs install -r requirements.txt