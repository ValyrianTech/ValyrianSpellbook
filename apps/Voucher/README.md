# Voucher service

This example shows how to make a simple Voucher service that will send a bitcoin transaction when a voucher is redeemed.

A HTTP POST trigger accepts new requests via the REST API, these requests include the voucher code and the address they
want the bitcoin sent too. 



Instructions:
-------------
* Modify the parameters section in the RedeemVoucher.py script to your needs  
* Run **setup_voucher.py**
* Send a HTTP POST request to the RedeemVoucher endpoint with the voucher code an a bitcoin address

Components:
-----------
* HTTP POST trigger
* python script
* SendTransaction (Send2Single) action
