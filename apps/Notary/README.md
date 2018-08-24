# Notary service

This example shows how to make a simple Notary service that will send a bitcoin transaction with an OP_RETURN message.

A HTTP POST trigger accepts new requests via the REST API, these requests include the message someone wants to have included in the Bitcoin blockchain. 
Each time a new request is received, the notary service generates a new address from the hot wallet to receive payment on. 

A new Balance trigger and SendTransaction action with the requested OP_RETURN message is created. 
This trigger also has a self-destruct timeout so if no payment is received within a specified time, the trigger and action will be deleted.

Once the trigger detect payment has been confirmed, the transaction with the OP_RETURN output is broadcasted.

Instructions:
-------------
* Modify the parameters section in the Notary.py script to your needs  
* Run **setup_notary.py**
* Send a HTTP POST request to the notary-request endpoint with the requested message to include in the Bitcoin blockchain as an OP_RETURN
* Send the payment for the request to the address given by the notary service
* Run **spellbook.py check_triggers** periodically (via a cron job)

Components:
-----------
* HTTP POST trigger
* python script
* SendTransaction (Send2Single) action
