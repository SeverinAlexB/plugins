#!/usr/bin/env python3
from binascii import hexlify
from onion import OnionPayload
from onion import TlvPayload
from pyln.client import Plugin, RpcError
import hashlib
import os
import struct
import time
import zbase32


plugin = Plugin()

TLV_KEYSEND_PREIMAGE = 5482373484
TLV_NOISE_MESSAGE = 34349334
TLV_NOISE_SIGNATURE = 34349335
TLV_NOISE_TIMESTAMP = 34349343


class Message(object):
    def __init__(self, sender, body, signature, payment=None, id=None):
        self.id = id
        self.sender = sender
        self.body = body
        self.signature = signature
        self.payment = payment
        self.verified = None

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "body": self.body,
            "signature": hexlify(self.signature).decode('ASCII'),
            "payment": self.payment.to_dict() if self.payment is not None else None,
            "verified": self.verified,
        }


class Payment(object):
    def __init__(self, payment_key, amount):
        self.payment_key = payment_key
        self.amount = amount

    def to_dict(self):
        return {
            "payment_key": hexlify(self.payment_key).decode('ASCII'),
            "payment_hash": hashlib.sha256(self.payment_key).hexdigest(),
            "amount": self.amount,
        }


def serialize_payload(n, blockheight):
    block, tx, out = n['channel'].split('x')
    payload = hexlify(struct.pack(
        "!cQQL", b'\x00',
        int(block) << 40 | int(tx) << 16 | int(out),
        int(n['msatoshi']),
        blockheight + n['delay'])).decode('ASCII')
    payload += "00" * 12
    return payload


def buildpath(payload, route):
    blockheight = plugin.rpc.getinfo()['blockheight']
    first_hop = route[0]
    # Need to shift the parameters by one hop
    hops = []
    for h, n in zip(route[:-1], route[1:]):
        # We tell the node h about the parameters to use for n (a.k.a. h + 1)
        hops.append({
            "type": "legacy",
            "pubkey": h['id'],
            "payload": serialize_payload(n, blockheight)
        })

    # The last hop has a special payload:
    hops.append({
        "type": "tlv",
        "pubkey": route[-1]['id'],
        "payload": hexlify(payload).decode('ASCII'),
    })
    return first_hop, hops, route


def deliver(payload, payment_hash, route):
    """Do your best to deliver `payload` to `node_id`.
    """
    payment_hash = hexlify(payment_hash).decode('ASCII')

    # plugin.log("Starting attempt {} to deliver message to {}".format(node_id))

    first_hop, hops, route = buildpath(payload, route)
    onion = plugin.rpc.createonion(hops=hops, assocdata=payment_hash)

    return {'route': route, 'payment_hash': payment_hash, 'success': False,
            'hops': hops, 'first_hop': first_hop}

    plugin.rpc.sendonion(onion=onion['onion'],
                         first_hop=first_hop,
                         payment_hash=payment_hash,
                         shared_secrets=onion['shared_secrets']
                         )
    try:
        plugin.rpc.waitsendpay(payment_hash=payment_hash)
        return {'route': route, 'payment_hash': payment_hash, 'success': True}
    except RpcError as e:
        failcode = e.error['data']['failcode']
        failingidx = e.error['data']['erring_index']
        if failcode == 16399 or failingidx == len(hops):
            return {'route': route, 'payment_hash': payment_hash, 'success': False,
                    'error': str(e.error), 'hops': hops, 'first_hop': first_hop}

    raise ValueError('Could not reach destination')


@plugin.async_method('keysend-to-route')
def keysend_to_route(route, request, **kwargs):
    payload = TlvPayload()

    payment_key = os.urandom(32)
    payment_hash = hashlib.sha256(payment_key).digest()

    payload.add_field(TLV_KEYSEND_PREIMAGE, payment_key)

    print('Keysend to route')
    print(f'Route: {route}')
    res = deliver(
        payload=payload.to_bytes(),
        route=route,
        payment_hash=payment_hash
    )
    request.set_result(res)


@plugin.init()
def init(configuration, options, plugin, **kwargs):
    print("Starting keysend-to-route plugin")


plugin.run()
