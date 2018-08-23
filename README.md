# BitcoinSpellbook-v0.3

The Bitcoin Spellbook is an Open Source platform that lets you create the back-end of your own Bitcoin application.

It is a configurable REST API where you can define triggers and actions. Think of it as something similar to IfThisThenThat but for Bitcoin.

When a trigger is activated, it runs a custom python script and\or predefined actions. The python script can also create or modify actions if needed.

Prerequisites
-------------

1. Python 2.7  
2. An [IPFS node](https://ipfs.io/docs/install/ "IPFS")  
3. Login credentials for a SMTP server (optional, needed for sending emails)
4. A [Blocktrail.com](https://www.blocktrail.com/) account (optional, needed if you want to use blocktrail as blockexplorer)


Instructions
------------

1. In the 'configuration' folder, you will find an example configuration file, fill in the required values and rename the file to '**Spellbook.conf**'  

2. Using the **hot_wallet.py** CLI, add the private keys of the addresses or the mnemonic seed of a BIP44 wallet that your app will use.  
You will need to provide a password to encrypt the hot wallet.
The wallet will be stored in encrypted format in the location that was specified in the configuration file.  
Each time the spellbookserver is started it will ask for the decryption password of the hot wallet. The password is only stored in memory, never written to file, and the hot wallet is only decrypted when a private key is needed.  
Run **hot_wallet.py -h** for more information.

3. Start the Bitcoin Spellbook server with **spellbookserver.py**

4. Add triggers and actions with the **spellbook.py** CLI. See **spellbook.py save_trigger -h** and **spellbook.py save_action -h** for more information.  
Take a look at the example apps in the 'apps' folder to get an idea of what is possible.  

5. Set up a cron that executes **spellbook.py check_triggers** (for example every 10 minutes) depending on the needs of your app, alternatively if you have a bitcoin node you could use the blocknotify option to run **spellbook.py check_triggers** each time a new block is found.


Run **spellbook.py -h** to get a list of all available subcommands.  
Each subcommand also has more detailed information which you can see by running **spellbook.py *subcommand* -h**

Triggers:
---------
* Balance, total received or total sent of an address
* Blockheight
* HTTP GET, POST and DELETE
* Manual
* Signed Message
* Timestamp
* Recurring
* TriggerStatus
* Dead mans' switch


Actions:
--------
* Run command
* Spawn process
* Send transaction
* Send email
* Webhook
* Delete trigger
* Reveal secret


Example apps:
-------------
A few example apps are provided to give you an idea how to get started.  
You can find these in the 'apps' directory.  
Run the setup script in the respective directory to initialize the app.  

**Note: these are just example apps and therefore have very limited features!**

* [Bitcoin splitter service](/apps/Splitter/)
* [Lottery](/apps/Lottery/)
* [Notary service](/apps/Notary/)
* [Dividends payout](/apps/Dividends/)
* [Payment processor](/apps/PaymentProcessor/) 

### Creating your own app
* Make a new python package in the 'apps' directory, don't forget the ´__init__.py´
* If your app needs to run a python script, copy the 'Template.py' script in the 'spellbookscripts' directory to the directory of your app.  
The name of the script must be exactly the same as the name of the class!
* Copy and modify a setup script of one of the example apps to easily create the needed triggers and actions


Other tools:
------------

### bitcoinwand.py
A CLI program that will sign a message or a file with the private key of an address and send the signature to a specific URL  
The private key of the address must be available in the hot wallet

Run **bitcoinwand.py -h** for more information
 
### transaction_listener.py
A CLI program that listens to newly broadcasted transactions and runs a command when an address on a watchlist receives or sends a transaction

Run **listeners\transaction_listener.py -h** for more information

### watchlist.py
A CLI program to manage a watchlist of addresses and specify which command needs to run when an address receives or sends a transaction

Run **listeners\watchlist.py -h** for more information

### hot_wallet.py
A CLI program to manage private keys and the mnemonic seed of a BIP44 wallet to use by the spellbook platform

**WARNING: Remember this is a HOT wallet and therefore should not be used to store large amounts of bitcoin!**


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


Donations
---------
[1Woutere8RCF82AgbPCc5F4KuYVvS4meW](https://www.blocktrail.com/BTC/address/1Woutere8RCF82AgbPCc5F4KuYVvS4meW)


Social Media:
-------------

Visit [www.valyrian.tech](http://www.valyrian.tech "Valyrian Tech") to keep up with the latest developments!

[Blog](https://medium.com/@wouterglorieux)

[Twitter: @WouterGlorieux](https://twitter.com/WouterGlorieux)

[LinkedIn](https://www.linkedin.com/in/wouterglorieux)