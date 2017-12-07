from dnschaind import validate, create_zone, TTL_1S, TTL_1Y, Qtype, TTL_1D
from dnschaind.zones import blockhash, blockheader, merkleproof
from dnschaind.services.bitcoin import INSTANCE as bitcoin


@validate(blockhash.QueryValidator)
def blockhash_resolver(query):
    block = bitcoin.getblockhash(int(query.arguments[0]))
    if not block:
        return
    response = blockhash.get_response(query, block['hash'])
    response.force_ttl = block['age'] > 6 and TTL_1Y or TTL_1S
    return response


@validate(blockheader.QueryValidator)
def blockheader_resolver(query):
    _hash = '0' * 8 + query.arguments[0]
    header = bitcoin.getblockheader(_hash)
    blockheight = blockheader and bitcoin.getblock(_hash)
    blockheight = blockheight is not None and blockheight['height']
    if not header:
        return
    return blockheader.get_response(query, header, blockheight)


@validate(merkleproof.QueryValidator)
def merkleproof_resolver(query):
    txhash = ''.join(query.arguments)
    txinfo = bitcoin.gettxinfo(txhash, blockparents=True)
    return merkleproof.get_response(query, txinfo)


zone = create_zone('btc', 'bitcoin')
zone.add_resolver('blockhash', blockhash_resolver, [Qtype.AAAA], ttl=TTL_1Y)
zone.add_resolver('blockheader', blockheader_resolver, [Qtype.TXT, Qtype.AAAA], ttl=TTL_1Y)
zone.add_resolver('merkleproof', merkleproof_resolver, [Qtype.A, Qtype.TXT, Qtype.CNAME], ttl=TTL_1D)

#zone.add_resolver('block', blockheader_resolver, [Qtype.A, Qtype.TXT, Qtype.CNAME], ttl=TTL_1W)

