# Bitcoin Splitter Service

This is a very simple app that will monitor the balance of a Bitcoin address and when the balance reaches a 
certain amount it will send a transaction to one or more predefined addresses, each address will receive a 
predefined share of the total amount.

This example will monitor the balance of the first address of the first account of the hot wallet and split 
the bitcoin it receives to the next 4 addresses in the hot wallet.

Instructions:
-------------
* Modify the parameters section in the setup_splitter.py script to your needs  
* Run **setup_splitter.py**
* Run **spellbook.py check_triggers Splitter** periodically (via a cron job)

Components:
-------------
* Balance trigger  
* SendTransaction (Send2Many) action  
