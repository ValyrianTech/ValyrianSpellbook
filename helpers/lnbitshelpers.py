import json
from time import sleep

import requests

LNBITS_URL = 'https://legend.lnbits.com'


def get_wallet_details(api_key: str) -> dict:
    """Get wallet details

    :param api_key: <string> API key of the wallet
    :return: 200 OK (application/json)
    {"id": <string>, "name": <string>, "balance": <int>}
    """
    url = f'{LNBITS_URL}/api/v1/wallet'
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'{response.text}')
        print(f'Request failed with status {response.status_code}')


def create_invoice(api_key: str, amount: int, memo: str, expiry: int, unit: str = 'btc', webhook: str = None, internal: bool = False) -> dict:
    """Create invoice

    :param api_key: <string> API key of the wallet
    :param amount: <float> Amount in satoshis
    :param memo: <string> Memo for the invoice
    :param expiry: <int> Expiry time in seconds
    :param unit: <string> Unit of the amount (default: btc)
    :param webhook: <string> Webhook URL (default: None)
    :param internal: <bool> Internal invoice (default: False)

    :return: Returns 201 CREATED (application/json)
    {"payment_hash": <string>, "payment_request": <string>, "checking_id": <string>, 'lnurl_response': <string>}
    """
    url = f'{LNBITS_URL}/api/v1/payments'
    headers = {'X-Api-Key': api_key}
    data = {
        'out': False,
        'amount': amount * 1e-8,
        'memo': memo,
        'expiry': expiry,
        'unit': unit,
        'webhook': webhook,
        'internal': internal
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        return response.json()
    else:
        print(f'{response.text}')
        print(f'Request failed with status {response.status_code}')


def decode_invoice(api_key: str, invoice: str) -> dict:
    """Decode invoice

    :param api_key: <string> API key of the wallet
    :param invoice: <string> Invoice to decode
    :return: Returns 200 OK (application/json)
    """
    url = f'{LNBITS_URL}/api/v1/payments/decode'
    headers = {'X-Api-Key': api_key}
    data = {'data': invoice}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        print(f'{response.text}')
        print(f'Request failed with status {response.status_code}')


def check_invoice(api_key: str, payment_hash: str) -> dict:
    """Check invoice

    :param api_key: <string> API key of the wallet
    :param payment_hash: <string> Payment hash of the invoice

    :return: Returns 200 OK (application/json)
    {"paid": <bool>, "preimage": <string>, "details": <dict>}
    """
    url = f'{LNBITS_URL}/api/v1/payments/{payment_hash}'
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'{response.text}')
        print(f'Request failed with status {response.status_code}')
