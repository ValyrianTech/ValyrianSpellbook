#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hmac
import copy

from helpers.py2specials import *
from helpers.py3specials import *

from helpers.privatekeyhelpers import privkey_to_pubkey, decode_privkey, get_privkey_format, encode_privkey
from helpers.publickeyhelpers import pubkey_to_address
from helpers.jacobianhelpers import fast_multiply, inv, G, N

from helpers.loghelpers import LOG

SIGHASH_ALL = 1
SIGHASH_NONE = 2
SIGHASH_SINGLE = 3
# this works like SIGHASH_ANYONECANPAY | SIGHASH_ALL, might as well make it explicit while
# we fix the constant
SIGHASH_ANYONECANPAY = 0x81

is_python2 = sys.version_info.major == 2


def make_custom_tx(private_keys, tx_inputs, tx_outputs, tx_fee=0, op_return_data=None):
    """
    Construct a custom transaction

    :param private_keys: a dict containing a key for each required address with the corresponding private key
    :param tx_inputs: a list of dicts containing the following keys: 'address', 'value', 'output' and 'confirmations'
                   output should be formatted as 'txid:i'
    :param tx_outputs: a list of dicts containing the keys 'address' and 'value'
    :param tx_fee: The total transaction fee in satoshis (The fee must be equal to the difference of the inputs and the outputs, this is an extra safety precaution)
    :param op_return_data: an optional message to add as an OP_RETURN output (max 80 chars)
    :return: A raw transaction
    """
    # Check if the transaction fee is valid
    if not isinstance(tx_fee, int) or tx_fee < 0:
        LOG.error('Invalid transaction fee: %d satoshis' % tx_fee)
        return

    # Check if the supplied fee is equal to the difference between the total input value and total output value
    total_input_value = sum([tx_input['value'] for tx_input in tx_inputs])
    total_output_value = sum([tx_output['value'] for tx_output in tx_outputs])

    if tx_fee != total_input_value - total_output_value:
        LOG.error('Transaction fee does not match the difference between the total input value and the total output value!')
        LOG.error('Total input: %s, Total output: %s, Transaction fee: %s' % (total_input_value, total_output_value, tx_fee))
        return

    # Check if all required private keys have been supplied
    all_keys_present = all([tx_input['address'] in private_keys for tx_input in tx_inputs])
    if not all_keys_present:
        LOG.error("At least 1 private key is missing.")
        return

    # Check if all inputs have at least 1 confirmation
    all_inputs_confirmed = all([tx_input['confirmations'] > 0 for tx_input in tx_inputs])
    if not all_inputs_confirmed:
        LOG.error("At least 1 input is unconfirmed.")
        return

    # Check if an OP_RETURN message needs to be added and if it is valid
    if isinstance(op_return_data, (str, unicode)) and len(op_return_data) > 80:
        LOG.error('OP_RETURN data is longer than 80 characters')
        return

    # All is good, make the transaction
    tx = mktx(tx_inputs, tx_outputs)

    # Add OP_RETURN message if necessary
    if isinstance(op_return_data, (str, unicode)):
        tx = add_op_return(op_return_data, tx)

    # Now sign each transaction input with the private key
    for i in range(0, len(tx_inputs)):
        tx = sign(tx, i, str(private_keys[tx_inputs[i]['address']]))

    return tx


# def send_tx(tx):
#     success = False
#     response = {}
#     try:
#         # retval = pybitcointools.blockr_pushtx(tx)
#         retval = {'status': 'success'}
#         logging.info("TX broadcast succeeded, Blockr response: %s" % str(retval))
#         response = json.loads(retval)
#     except Exception as e:
#         logging.error("TX broadcast failed: %s" % str(e))
#
#     if 'status' in response and response['status'] == 'success':
#         success = True
#
#     return success


# extra functions for op_return from a fork of pybitcointools
# https://github.com/wizardofozzie/pybitcointools


def num_to_op_push(x):
    x = int(x)
    if 0 <= x <= 75:
        pc = ''
        num = encode(x, 256, 1)
    elif x < 0xff:
        pc = from_int_to_byte(0x4c)
        num = encode(x, 256, 1)
    elif x < 0xffff:
        pc = from_int_to_byte(0x4d)
        num = encode(x, 256, 2)[::-1]
    elif x < 0xffffffff:
        pc = from_int_to_byte(0x4e)
        num = encode(x, 256, 4)[::-1]
    else:
        raise ValueError("0xffffffff > value >= 0")
    return pc + num


def wrap_script(hexdata):
    if re.match('^[0-9a-fA-F]*$', hexdata):
        return binascii.hexlify(wrap_script(binascii.unhexlify(hexdata)))
    return num_to_op_push(len(hexdata)) + hexdata


def add_op_return(msg, tx_hex=None):
    """Makes OP_RETURN script from msg, embeds in Tx hex"""
    hex_data = binascii.hexlify(b'\x6a' + wrap_script(msg))

    if tx_hex is None:
        return hex_data
    else:
        if not re.match("^[0-9a-fA-F]*$", tx_hex):
            return binascii.unhexlify(add_op_return(msg, binascii.hexlify(tx_hex)))
        elif isinstance(tx_hex, dict):
            txo = tx_hex
            outs = txo.get('outs')
        else:
            outs = deserialize(tx_hex).get('outs')

        txo = deserialize(tx_hex)
        assert (len(outs) > 0) and sum(multiaccess(outs, 'value')) > 0 \
            and not any([o for o in outs if o.get("script")[:2] == '6a']), \
            "Tx limited to *1* OP_RETURN, and only whilst the other outputs send funds"
        txo['outs'].append({'script': hex_data, 'value': 0})
        return serialize(txo)


# copied from pybitcointools

def serialize(txobj):
    # if isinstance(txobj, bytes):
    #    txobj = bytes_to_hex_string(txobj)
    o = []
    if json_is_base(txobj, 16):
        json_changedbase = json_changebase(txobj, lambda x: binascii.unhexlify(x))
        hexlified = safe_hexlify(serialize(json_changedbase))
        return hexlified
    o.append(encode(txobj["version"], 256, 4)[::-1])
    o.append(num_to_var_int(len(txobj["ins"])))
    for inp in txobj["ins"]:
        o.append(inp["outpoint"]["hash"][::-1])
        o.append(encode(inp["outpoint"]["index"], 256, 4)[::-1])
        o.append(num_to_var_int(len(inp["script"]))+(inp["script"] if inp["script"] or is_python2 else bytes()))
        o.append(encode(inp["sequence"], 256, 4)[::-1])
    o.append(num_to_var_int(len(txobj["outs"])))
    for out in txobj["outs"]:
        o.append(encode(out["value"], 256, 8)[::-1])
        o.append(num_to_var_int(len(out["script"]))+out["script"])
    o.append(encode(txobj["locktime"], 256, 4)[::-1])

    return ''.join(o) if is_python2 else reduce(lambda x,y: x+y, o, bytes())


def deserialize(tx):
    if isinstance(tx, str) and re.match('^[0-9a-fA-F]*$', tx):
        # tx = bytes(bytearray.fromhex(tx))
        return json_changebase(deserialize(binascii.unhexlify(tx)),
                               lambda x: safe_hexlify(x))
    # http://stackoverflow.com/questions/4851463/python-closure-write-to-variable-in-parent-scope
    # Python's scoping rules are demented, requiring me to make pos an object
    # so that it is call-by-reference
    pos = [0]

    def read_as_int(bytez):
        pos[0] += bytez
        return decode(tx[pos[0] - bytez:pos[0]][::-1], 256)

    def read_var_int():
        pos[0] += 1

        val = from_byte_to_int(tx[pos[0] - 1])
        if val < 253:
            return val
        return read_as_int(pow(2, val - 252))

    def read_bytes(bytez):
        pos[0] += bytez
        return tx[pos[0] - bytez:pos[0]]

    def read_var_string():
        size = read_var_int()
        return read_bytes(size)

    obj = {"ins": [], "outs": [], "version": read_as_int(4)}
    ins = read_var_int()
    for i in range(ins):
        obj["ins"].append({
            "outpoint": {
                "hash": read_bytes(32)[::-1],
                "index": read_as_int(4)
            },
            "script": read_var_string(),
            "sequence": read_as_int(4)
        })
    outs = read_var_int()
    for i in range(outs):
        obj["outs"].append({
            "value": read_as_int(8),
            "script": read_var_string()
        })
    obj["locktime"] = read_as_int(4)
    return obj


def access(obj, prop):
    if isinstance(obj, dict):
        if prop in obj:
            return obj[prop]
        elif '.' in prop:
            return obj[float(prop)]
        else:
            return obj[int(prop)]
    else:
        return obj[int(prop)]


def multiaccess(obj, prop):
    return [access(o, prop) for o in obj]


def mktx(*args):
    # [in0, in1...],[out0, out1...] or in0, in1 ... out0 out1 ...
    ins, outs = [], []
    for arg in args:
        if isinstance(arg, list):
            for a in arg: (ins if is_inp(a) else outs).append(a)
        else:
            (ins if is_inp(arg) else outs).append(arg)

    txobj = {"locktime": 0, "version": 1, "ins": [], "outs": []}
    for i in ins:
        if isinstance(i, dict) and "outpoint" in i:
            txobj["ins"].append(i)
        else:
            if isinstance(i, dict) and "output" in i:
                i = i["output"]
            txobj["ins"].append({
                "outpoint": {"hash": i[:64], "index": int(i[65:])},
                "script": "",
                "sequence": 4294967295
            })
    for o in outs:
        if isinstance(o, string_or_bytes_types):
            addr = o[:o.find(':')]
            val = int(o[o.find(':')+1:])
            o = {}
            if re.match('^[0-9a-fA-F]*$', addr):
                o["script"] = addr
            else:
                o["address"] = addr
            o["value"] = val

        outobj = {}
        if "address" in o:
            outobj["script"] = address_to_script(o["address"])
        elif "script" in o:
            outobj["script"] = o["script"]
        else:
            raise Exception("Could not find 'address' or 'script' in output.")
        outobj["value"] = o["value"]
        txobj["outs"].append(outobj)

    return serialize(txobj)


def sign(tx, i, priv, hashcode=SIGHASH_ALL):
    i = int(i)
    if (not is_python2 and isinstance(re, bytes)) or not re.match('^[0-9a-fA-F]*$', tx):
        return binascii.unhexlify(sign(safe_hexlify(tx), i, priv))

    if len(priv) <= 33:
        priv = safe_hexlify(priv)

    pub = privkey_to_pubkey(priv)
    address = pubkey_to_address(pub)
    signing_tx = signature_form(tx, i, p2pkh_script(address), hashcode)
    sig = ecdsa_tx_sign(signing_tx, priv, hashcode)
    txobj = deserialize(tx)
    txobj["ins"][i]["script"] = serialize_script([sig, pub])

    return serialize(txobj)


def is_inp(arg):
    return len(arg) > 64 or "output" in arg or "outpoint" in arg


def json_is_base(obj, base):
    if not is_python2 and isinstance(obj, bytes):
        return False

    alpha = get_code_string(base)
    if isinstance(obj, string_types):
        for i in range(len(obj)):
            if alpha.find(obj[i]) == -1:
                return False
        return True
    elif isinstance(obj, int_types) or obj is None:
        return True
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if not json_is_base(obj[i], base):
                return False
        return True
    else:
        for x in obj:
            if not json_is_base(obj[x], base):
                return False
        return True


def json_changebase(obj, changer):
    if isinstance(obj, string_or_bytes_types):
        return changer(obj)
    elif isinstance(obj, int_types) or obj is None:
        return obj
    elif isinstance(obj, list):
        return [json_changebase(x, changer) for x in obj]

    return dict((x, json_changebase(obj[x], changer)) for x in obj)


def num_to_var_int(x):
    x = int(x)
    if x < 253:
        return from_int_to_byte(x)
    elif x < 65536:
        return from_int_to_byte(253)+encode(x, 256, 2)[::-1]
    elif x < 4294967296:
        return from_int_to_byte(254) + encode(x, 256, 4)[::-1]
    else:
        return from_int_to_byte(255) + encode(x, 256, 8)[::-1]


def b58check_to_hex(address):
    """
    Convert a base58check string to hexadecimal format

    :param address: A Bitcoin address
    :return: A base58check string in hexadecimal format
    """
    return safe_hexlify(b58check_to_bin(address))


def b58check_to_bin(address):
    """
    Do a base58 check on the address and return the address minus first byte and the checksum (last 4 bytes) in binary format

    :param address: A Bitcoin address
    :return: A base58check string in binary format
    """
    leadingzbytes = len(re.match('^1*', address).group(0))  # number of leading zero bytes (1 == 0 in base58)
    data = b'\x00' * leadingzbytes + changebase(address, 58, 256)
    assert bin_dbl_sha256(data[:-4])[:4] == data[-4:]

    return data[1:-4]


def p2sh_script(address):
    """
    Make a Pay-To-Script-Hash (P2SH) script
    This is the type of scripts used by multisig addresses -> starting with 3 (mainnet) or 2 (testnet)

    OP_HASH160 <redeemScriptHash> OP_EQUAL
    
    a9         14             89 AB CD EF AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA    87
    OP_HASH160 Bytes to push  Data to push                                                   OP_EQUAL
               14 hex = 20 bytes

    :param address: A Bitcoin address
    :return: a P2SH script
    """
    return 'a914' + b58check_to_hex(address) + '87'


def p2pkh_script(address):
    """
    Make a Pay-To-Public-Key-Hash (P2PKH) script
    This is the type of script old legacy addresses use -> starting with 1 (mainnet) or m or n (testnet)

    OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG

    76      a9            14             89 AB CD EF AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA   88              ac
    OP_DUP OP_HASH160    Bytes to push   Data to push                                                  OP_EQUALVERIFY OP_CHECKSIG
                         14 hex = 20 bytes

    :param address: A Bitcoin address
    :return: a P2PKH script
    """
    return '76a914' + b58check_to_hex(address) + '88ac'


def p2wpkh_script(address):
    """
    Make a Pay-To-Witness-Public-Key-Hash (P2WPKH) script
    This is the type of script used by the new bech32 addresses -> starting with bc1 (mainnet) or tb1 (testnet)

    0 <pubKeyHash>

    00 14            89 AB CD EF AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA
    0  Bytes to push Data to push

    14 hex = 20 bytes

    :param address: A Bitcoin address
    :return: a P2WPKH script
    """
    return '0014' + b58check_to_hex(address)


def p2wsh_script(address):
    """
    Make a Pay-To-Witness-Script-Hash (P2WSH) script
    This is the type of script used by the new bech32 addresses (multisig) -> starting with bc1 (mainnet) or tb1 (testnet)

    0 <script hash>

    00 20            89 AB CD EF AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA AB BA
    0  Bytes to push Data to push

    20 hex = 32 bytes

    :param address: A Bitcoin address
    :return: a P2WPKH script
    """
    return '0020' + b58check_to_hex(address)


def address_to_script(address):
    """
    Make the script based on the address

    :param address: a Bitcoin address
    :return: a P2SH or P2PKH script
    """
    if address[0] == '3' or address[0] == '2':
        return p2sh_script(address)
    else:
        return p2pkh_script(address)


def signature_form(tx, i, script, hashcode=SIGHASH_ALL):
    i, hashcode = int(i), int(hashcode)
    if isinstance(tx, string_or_bytes_types):
        return serialize(signature_form(deserialize(tx), i, script, hashcode))

    newtx = copy.deepcopy(tx)
    for inp in newtx["ins"]:
        inp["script"] = ""

    newtx["ins"][i]["script"] = script
    if hashcode == SIGHASH_NONE:
        newtx["outs"] = []
    elif hashcode == SIGHASH_SINGLE:
        newtx["outs"] = newtx["outs"][:len(newtx["ins"])]
        for out in newtx["outs"][:len(newtx["ins"]) - 1]:
            out['value'] = 2**64 - 1
            out['script'] = ""
    elif hashcode == SIGHASH_ANYONECANPAY:
        newtx["ins"] = [newtx["ins"][i]]
    else:
        pass

    return newtx


if is_python2:
    def serialize_script(script):
        if json_is_base(script, 16):
            return binascii.hexlify(serialize_script(json_changebase(script,
                                                                     lambda x: binascii.unhexlify(x))))
        return ''.join(map(serialize_script_unit, script))
else:
    def serialize_script(script):
        if json_is_base(script, 16):
            return safe_hexlify(serialize_script(json_changebase(script,
                                                                 lambda x: binascii.unhexlify(x))))

        result = bytes()
        for b in map(serialize_script_unit, script):
            result += b if isinstance(b, bytes) else bytes(b, 'utf-8')
        return result


def serialize_script_unit(unit):
    if isinstance(unit, int):
        if unit < 16:
            return from_int_to_byte(unit + 80)
        else:
            return from_int_to_byte(unit)
    elif unit is None:
        return b'\x00'
    else:
        if len(unit) <= 75:
            return from_int_to_byte(len(unit))+unit
        elif len(unit) < 256:
            return from_int_to_byte(76)+from_int_to_byte(len(unit))+unit
        elif len(unit) < 65536:
            return from_int_to_byte(77)+encode(len(unit), 256, 2)[::-1]+unit
        else:
            return from_int_to_byte(78)+encode(len(unit), 256, 4)[::-1]+unit


def der_encode_sig(v, r, s):
    b1, b2 = safe_hexlify(encode(r, 256)), safe_hexlify(encode(s, 256))

    if len(b1) and b1[0] in '89abcdef':
        b1 = '00' + b1

    if len(b2) and b2[0] in '89abcdef':
        b2 = '00' + b2

    left = '02'+encode(len(b1)//2, 16, 2)+b1
    right = '02'+encode(len(b2)//2, 16, 2)+b2

    return '30'+encode(len(left+right)//2, 16, 2)+left+right


def ecdsa_tx_sign(tx, priv, hashcode=SIGHASH_ALL):
    rawsig = ecdsa_raw_sign(bin_txhash(tx, hashcode), priv)
    return der_encode_sig(*rawsig)+encode(hashcode, 16, 2)


def ecdsa_raw_sign(msghash, priv):

    z = hash_to_int(msghash)
    k = deterministic_generate_k(msghash, priv)

    r, y = fast_multiply(G, k)
    s = inv(k, N) * (z + r*decode_privkey(priv)) % N

    v, r, s = 27+((y % 2) ^ (0 if s * 2 < N else 1)), r, s if s * 2 < N else N - s
    if 'compressed' in get_privkey_format(priv):
        v += 4

    return v, r, s


def hash_to_int(string):
    """
    Convert a hash string to an integer

    :param string: a hash string
    :return: an integer
    """
    if len(string) in [40, 64]:
        return decode(string, 16)

    return decode(string, 256)


def deterministic_generate_k(msghash, priv):
    v = b'\x01' * 32
    k = b'\x00' * 32
    priv = encode_privkey(priv, 'bin')
    msghash = encode(hash_to_int(msghash), 256, 32)
    k = hmac.new(k, v+b'\x00'+priv+msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v+b'\x01'+priv+msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()

    return decode(hmac.new(k, v, hashlib.sha256).digest(), 256)


def bin_txhash(tx, hashcode=None):
    """
    Get the transaction hash (txid) in binary format

    :param tx: The transaction
    :param hashcode: SIGHASH_ALL = 1, SIGHASH_NONE = 2, SIGHASH_SINGLE = 3, SIGHASH_ANYONECANPAY = 0x81
    :return: a transaction hash (txid) in binary format
    """
    return binascii.unhexlify(txhash(tx, hashcode))


def txhash(tx, hashcode=None):
    """
    Get the transaction hash (txid)

    :param tx: The transaction
    :param hashcode: SIGHASH_ALL = 1, SIGHASH_NONE = 2, SIGHASH_SINGLE = 3, SIGHASH_ANYONECANPAY = 0x81
    :return: a transaction hash (txid) in hexadecimal format
    """
    if isinstance(tx, str) and re.match('^[0-9a-fA-F]*$', tx):
        tx = changebase(tx, 16, 256)

    # [::-1] means the same as the list in reverse order
    if hashcode:
        return double_sha256(from_string_to_bytes(tx) + encode(int(hashcode), 256, 4)[::-1])
    else:
        return safe_hexlify(bin_dbl_sha256(tx)[::-1])


def double_sha256(string):
    """
    Do a double SHA256 hash on a string

    :param string: A string
    :return: The hash in hexadecimal format
    """
    return safe_hexlify(bin_dbl_sha256(string))
