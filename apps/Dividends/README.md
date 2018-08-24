# Dividends payout

Lets say that you want to do a crowdfunding to raise money for a project. Anyone who wants to back your project can do so 
by simply sending bitcoin to a specific address (lets call this the investors address).

Important: investors should only send from a bitcoin address that they have the keys for, because the address that sends is also the 
address that will receive the dividends. So don't send directly from an online wallet. Also don't send from bech32 addresses for now.

The Simplified Inputs List (SIL) of this address gives an easy list of all the investors and their share.

When the project wants to give out dividends, a second address (lets call this the dividends address), is monitored by a Balance trigger.
Each time the balance in the dividends address reaches a certain amount, all the available funds (minus an optional fee) are 
distributed to the SIL of the investors address.

It is also possible to lock the investors' shares at a specific block height.

Instructions:
-------------
* Modify the parameters section in the setup_dividends.py script to your needs  
* Run **setup_dividends.py**
* Run **spellbook.py check_triggers Dividends** periodically (via a cron job)

Components:
-------------
* Balance trigger
* SendTransaction (Send2SIL) action
