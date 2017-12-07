from dnschaind import validate, create_zone, TTL_1S, TTL_1Y, Qtype
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
    header = bitcoin.getblockheader(blockhash, verbose=False)
    if not header:
        return
    return blockheader.get_response(query, header)


@validate(merkleproof.QueryValidator)
def merkleproof_resolver(query):
    txhash = ''.join(query.arguments)
    txinfo = bitcoin.gettxinfo(txhash, blockparents=True)
    return merkleproof.get_response(query, txinfo)


zone = create_zone('btc', 'bitcoin')
zone.add_resolver('blockhash', blockhash_resolver, [Qtype.AAAA], ttl=TTL_1Y)


#zone.add_resolver('block', blockheader_resolver, [Qtype.A, Qtype.TXT, Qtype.CNAME], ttl=TTL_1W)
#zone.add_resolver('merkle', merkleproof_resolver, [Qtype.A, Qtype.TXT, Qtype.CNAME], ttl=TTL_1W)
