#!/usr/bin/env python3
from binascii import hexlify

from mylogger import get_my_logger
from onion import TlvPayload
from pyln.client import Plugin, RpcError
import hashlib
import os
import struct

from primitives import varint_encode_direct

logger = get_my_logger()

plugin = Plugin()

TLV_KEYSEND_PREIMAGE = 5482373484
'''
type: 2 (amt_to_forward)
data:
[tu64:amt_to_forward]
'''
TLV_AMT_TO_FORWARD = 2
'''
type: 4 (outgoing_cltv_value)
data:
[tu32:outgoing_cltv_value]
'''
TLV_OUTGOING_CLTV_VALUE = 4

'''
type: 8 (payment_data)
data:
[32*byte:payment_secret]
[tu64:total_msat]
'''
TLV_PAYMENT_DATA = 8



def serialize_payload(n, blockheight):
    block, tx, out = n['channel'].split('x')
    long_channel_id = int(block) << 40 | int(tx) << 16 | int(out)
    msat = int(n['msatoshi'])
    bh = blockheight + n['delay']

    logger.debug(f'Payload of {n["channel"]}: {long_channel_id}, {msat}, {bh}')
    payload = hexlify(struct.pack(
        "!cQQL", b'\x00',
        long_channel_id,
        msat,
        bh)).decode('ASCII')
    payload += "00" * 12
    return payload


def buildpath(payload, route, blockheight):
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


def deliver(payload, payment_hash, route, blockheight):
    """Do your best to deliver `payload` to `node_id`.
    """
    payment_hash = hexlify(payment_hash).decode('ASCII')

    first_hop, hops, route = buildpath(payload, route, blockheight)
    logger.info(f'Firsthop: {first_hop}, hops: {hops}')
    onion = plugin.rpc.createonion(hops=hops, assocdata=payment_hash)

    plugin.rpc.sendonion(onion=onion['onion'],
                         first_hop=first_hop,
                         payment_hash=payment_hash,
                         shared_secrets=onion['shared_secrets']
                         )
    logger.info('Onion sent')
    try:
        plugin.rpc.waitsendpay(payment_hash=payment_hash)
        logger.info('Success')
        return {'route': route, 'payment_hash': payment_hash, 'success': True}
    except RpcError as e:
        failcode = e.error['data']['failcode']
        failingidx = e.error['data']['erring_index']
        logger.info(f'waitsendpay error: failcode: {failcode}, failingidx: {failingidx}')
        logger.error(str(e.error))
        if failcode == 16399 and failingidx == len(hops):
            return {'keysendUnsupported': True}
        else:
            return {'route': route, 'payment_hash': payment_hash, 'success': False,
                'error': str(e.error), 'hops': hops, 'first_hop': first_hop}


def construct_final_payload(payment_key, route, blockheight):
    payload = TlvPayload()
    payload.add_field(TLV_KEYSEND_PREIMAGE, payment_key)

    amount_msat = route[-1]['msatoshi']
    payload.add_field(TLV_AMT_TO_FORWARD, varint_encode_direct(amount_msat))

    outgoing_cltv = blockheight + route[-1]['delay']
    payload.add_field(TLV_OUTGOING_CLTV_VALUE, varint_encode_direct(outgoing_cltv))

    # value = payment_key + varint_encode_direct(amount_msat)
    # payload.add_field(TLV_PAYMENT_DATA, value)
    return payload


@plugin.method('keysend-to-route')
def keysend_to_route(route,  **kwargs):
    amountMsat = route[-1]['msatoshi']
    logger.info('-----')
    logger.info('----- Keysend to route started ------')
    logger.info(f'Route: {route}')
    logger.info(f'{amountMsat}msat to send to destination')

    blockheight = plugin.rpc.getinfo()['blockheight']

    payment_key = os.urandom(32)
    payment_hash = hashlib.sha256(payment_key).digest()

    payload = construct_final_payload(payment_key, route, blockheight)

    logger.info(f'Payload: {payload}')

    res = deliver(
        payload=payload.to_bytes(),
        route=route,
        payment_hash=payment_hash,
        blockheight=blockheight
    )
    return res


@plugin.init()
def init(configuration, options, plugin, **kwargs):
    print("Starting keysend-to-route plugin")


plugin.run()
