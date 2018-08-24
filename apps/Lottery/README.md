# Lottery

This example app shows how to make a basic lottery.

A Block_height trigger is created to activate at a certain block_height + a number of confirmations (the confirmations are to ensure there has not been a chain reorg)

A SendTransaction action is created with almost all info it needs to run, such as which address is the lottery address and how much of a lottery fee will be subtracted from the winnings.
The receiving address of the SentTransaction is not filled in yet, because we don't know who the winner will be.

Anyone who wants to participate in the lottery only has to send a transaction to the lottery address before the given block height. 
The higher the amount that is sent, the more 'tickets' they get. If a transaction is not included in a block in or before the given block height,
then that transaction will not count.

When the Block_height trigger activates, it first runs a python script.
This python script determines the winner via a random_address_from_SIL() method and modifies the action to set the receiving address.

The winner is determined by using the block hash of the predefined block height as a random number and choosing a random address 
from the Simplified Inputs List (SIL) of the lottery address at the predefined block height.

The winner then receives all the bitcoin sent to the lottery address (minus a fee for the operator of the service)

Instructions:
-------------
* Modify the parameters section in the setup_lottery.py script to your needs  
* Run **setup_lottery.py**
* Run **spellbook.py check_triggers Lottery** periodically (via a cron job)

Components:
-----------
* Block_height trigger
* python script
* SendTransaction (Send2Single) action

