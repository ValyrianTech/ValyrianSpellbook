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

1. In the 'configuration' folder, you will find an example configuration file, fill in the required values and rename the file to '**spellbook.conf**'  

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

#### Balance, Received and Sent
These triggers activate when the final balance (or total received or total sent) of an address is at least a certain amount.  

parameters:
* address: string (a bitcoin address)
* amount: integer (in satoshis)

#### Blockheight
This trigger activates when the Bitcoin blockchain reaches a certain height plus a number of confirmations

parameters:
* block_height: integer
* confirmations: integer

#### HTTP GET, POST and DELETE
These triggers activate when a HTTP GET, POST or DELETE request is received. It is possible to pass data with each of these types of http requests.

Note: The endpoints created by these triggers look like:  
GET: /spellbook/triggers/*trigger-id*/get  
POST: /spellbook/triggers/*trigger-id*/post  
DELETE: /spellbook/triggers/*trigger-id*/delete

parameters:  
None


#### Manual
This trigger only activates when a GET request is received at: *spellbook-url*/spellbook/trigger/*trigger-id*/activate
This request requires authentication via a api key and api secret.  
The **spellbook.py activate_trigger** command will do all of this for you. 

parameters:  
None

#### Signed Message
This trigger will activate when it receives a GET request containing a message and signature and an address.
It will verify that the message is indeed signed by the address and only activates if it is valid.

The address parameter is optional: when specified, the trigger will only accept messages from that address. If the address parameter 
is omitted, all addresses are allowed.

parameters:  
* address: string (a bitcoin address)


#### Timestamp
This trigger activates when a given timestamp is reached. 

Note: The trigger will NOT activate at EXACTLY that timestamp, but when **spellbook.py check_triggers** is run. Keep this in mind when setting up cron jobs!

parameters:  
* timestamp: integer (unix timestamp)

#### Recurring
This trigger will activate periodically between a begin_time and end_time.

Note: The trigger will NOT activate at EXACTLY that timestamp, but when **spellbook.py check_triggers** is run. Keep this in mind when setting up cron jobs!


parameters:  
* begin_time: integer (unix timestamp)
* end_time: integer (unix timestamp)
* interval: integer (in seconds)

#### TriggerStatus
This trigger activate based on the success or failure of another trigger. 
It can be used to create fallback mechanisms in case something goes wrong

parameters:  
* previous_trigger: string (a trigger_id)
* previous_trigger_status: string ('Succeeded' or 'Failed')

#### Dead mans' switch
This trigger activates a certain time after it has been armed and it is not reset before the timeout is reached.
A warning email will be sent when the timeout is at 50%, 75% and at 90%.

To arm the trigger: use the **spellbook.py activate_trigger trigger_id** command  
To reset the trigger: use the **spellbook.py save_trigger trigger_id --reset** command  

Once the trigger is armed, the only way to fully deactivate it is to delete the trigger with the **spellbook.py delete_trigger trigger_id** command


parameters:  
* timeout: integer (in seconds)
* warning_email: string (an email address)


Scripts:
--------
You can add your own script by copying the 'Template.py' script from the spellbookscripts directory to the directory of your app

Rename the file and make sure to use exactly the same name for the class inside the script. The class must be derived from the spellbookscript class.

Write your code in the run() method, this will be executed before any actions are done.

Optionally, you can write code in the cleanup() method, this will be executed after all actions are done.



Actions:
--------
#### Command and SpawnProcess
These actions will execute a given command. The difference between the two is that a Command action will run the command in the same process as the spellbookserver. 
Whereas the SpawnProcess will first spawn a new child process to run the command in.  

A Command action can be useful for commands that only take a short amount of time and the rest of the script must wait until it is finished.  

A SpawnProcess action can be useful for commands that take a long time or when multiple processes in parallel are needed because this type of action will not block the execution of the spellbookserver.  

parameters:
* run_command: string


#### Send transaction
This action will send a bitcoin transaction.  

The transaction can either send a specific amount or all the available funds in an address.  

Each type of transaction also allows adding a special spellbook fee based on a percentage of the sending amount (Optional)  

A change address can be specified, but is not necessary, if there is change and no change_address, the sending address will receive the change.

The wallet_type can be 'BIP44' or 'Single', the private keys for the sending address must be available in the hot wallet.  

Optionally, an OP_RETURN output can be added as well.

Each of the types allows the following parameters:

* transaction_type: string (Send2Single, Send2Many, Send2SIL, Send2LBL, Send2LRL, Send2LSL or Send2LAL)
* amount: integer (in Satoshis)
* minimum_amount: integer (in Satoshis)
* fee_address: string (a bitcoin address)
* fee_percentage: float (a float between 0.0 and 100.0)
* wallet_type: string ('BIP44' or 'Single')
* sending_address: string (a bitcoin adddress)
* bip44_account: integer 
* bip44_index: integer
* change_address: string (a bitcoin address)
* op_return_data: string (max 80 characters)

There are several types of transactions:

###### Send2Single
A simple transaction to a single address, might also include a spellbook fee and/or a change_address.

parameters specific to this transaction type:
* receiving_address (a bitcoin address)


###### Send2Many
A transaction to multiple addresses based on a given distribution, might also include a spellbook fee and/or a change_address

parameters specific to this transaction type:   
* distribution: dict containing address-value pairs

###### Send2SIL
Similar to a Send2Many transaction, but will use the SIL (Simplified Inputs List) as the distribution for the receiving addresses and amounts

parameters specific to this transaction type:   
* registration_address: string (a bitcoin address)
* registration_block_height: integer


###### Send2LBL, Send2LRL, Send2LSL
Similar to a Send2Many transaction, but will use a LBL (Linked Balance List), LRL (Linked Received List) or LSL (Linked Sent List) as the distribution for the receiving addresses and amounts

parameters specific to this transaction type:   
* registration_address: string (a bitcoin address)
* registration_block_height: integer
* registration_xpub: string (a xpub key)

###### Send2LAL
Similar to a Send2Many transaction, but will send each of the available utxos to the corresponding address in the LAL (Linked Address List)

parameters specific to this transaction type:   
* registration_address: string (a bitcoin address)
* registration_block_height: integer
* registration_xpub: string (a xpub key)

#### Send email
This action will send an email with given subject to given address, the body of the email is based of a template file.
The body template can contain placeholder values, but currently these can only be specified via a spellbookscript.

parameters:
* mail_subject: string
* mail_recipients: string (email addresses separated with ';')
* mail_body_template: string (filename of the template)

#### Webhook
This action will make a HTTP GET request to a given webhook url.

parameters:
* webhook: string (a url)

#### Reveal secret
This action will allow the revealing of a secret text or url when requested via a GET request to /spellbook/actions/*action_id*/reveal  
Before the action is run, no information will be returned.

parameters:
* reveal_text: string 
* reveal_link: string (a url)


Example apps:
-------------
A few example apps are provided to give you an idea how to get started.  
You can find these in the 'apps' directory.  
Run the setup script in the respective directory to initialize the app.  

**Note: these are just example apps and therefore have very limited features!**

* [Bitcoin splitter service](./apps/Splitter/)
* [Lottery](./apps/Lottery/)
* [Notary service](./apps/Notary/)
* [Dividends payout](./apps/Dividends/)
* [Payment processor](./apps/PaymentProcessor/) 

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

[Blog](https://medium.com/@valyriantech)

[Twitter: @WouterGlorieux](https://twitter.com/WouterGlorieux)

[LinkedIn](https://www.linkedin.com/in/wouterglorieux)