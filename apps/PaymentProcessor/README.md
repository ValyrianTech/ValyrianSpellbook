# Payment Processor

This example shows how to make a very basic payment processor.

Via a HTTP POST request new payment request can be made, these request contain information such as a seller_id, the amount in fiat, the currency and an optional note.

The payment processor calculates the required amount in BTC and then generates a new address from the hot wallet and 
spawns a new process to listen for the payment transaction. The response of the HTTP POST request includes all the information needed to make the payment.  

Besides the listener process, a new trigger is also created to monitor the balance of the payment address, this is to 
check for confirmations and also acts as a fallback mechanism in case the listener doesn't pick up the transaction.

The listener process will only listen for a certain amount of time before it times out. This is to prevent too many processes at the same time.
When the listener detects the transaction it will notify the payment processor with the txid. The payment processor then checks if the payment is valid.
If the payment is valid, a first email is sent to the payment processor operator to notify a transaction is received. After 6 confirmations have happened, 
a second email will be sent.

Via a HTTP GET request the status of a payment can be requested. Once the payment is fully confirmed, 
the trigger and actions that were created for the request will self-destruct.

Instructions:
-------------
* Modify the parameters section in the paymentprocessorscript.py script to your needs  
* Run **setup_payment_processor.py**
* Send a HTTP POST request to the PaymentProcessorNewPayment endpoint with the details of the payment request
* Send the payment for the request to the address given by the payment processor service
* Run **spellbook.py check_triggers** periodically (via a cron job)

Components:
-------------
* A HTTP POST trigger to accept new payment requests.
* A HTTP GET trigger to get the status of a payment.
* A HTTP POST trigger to be notified of a payment (only used by the listener process)
* A python script for each HTTP request trigger
* A listener process
* Balance trigger
* SendMail action
