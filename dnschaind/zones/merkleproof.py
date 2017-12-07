import binascii
from dnschaind.dnschain import exceptions
from dnschaind import get_data_chunks, int_to_ipv6, SatoshiMerkleTree, estimate_chunks, base64encode, check_merkle_proof


def query_validator(query):
    try:
        qa = len(query.arguments)
        if qa < 2:
            raise exceptions.MissingArgumentsException(query)
        elif qa == 2:
            assert all([16 == len(binascii.unhexlify(x.encode())) for x in query.arguments])
        elif qa == 3:
            assert all([16 == len(binascii.unhexlify(x.encode())) for x in query.arguments[:2]])
            assert int(query.arguments[2]) < 256
        else:
            raise exceptions.InvalidArgumentsException(query)
    except (AssertionError, binascii.Error, ValueError) as e:
        raise exceptions.InvalidArgumentsException(query) from e

QueryValidator = query_validator


def get_merkle_tree(txs):
    transactions = [binascii.hexlify(binascii.unhexlify(t)[::-1]).decode() for t in txs]
    tree = SatoshiMerkleTree(transactions, prehashed=True)
    tree.build()
    return tree


def get_merkle_proof(tx, txs):
    e = {'SELF': chr(0).encode(), 'R': chr(1).encode(), 'L': chr(2).encode()}
    tree = get_merkle_tree(txs)
    index = txs.index(tx)
    chain = tree.get_chain(index)
    proof = b''
    for c in chain:
        proof += b'' if c[1] == 'ROOT' else c[0] + e[c[1]]
    return proof


def get_response(query, txinfo):
    from dnschaind import Response
    response = Response()
    data = txinfo.get('blockparents') and get_merkle_proof(txinfo['txid'], txinfo['blockparents'])
    if not data:
        return response
    chunk = get_data_chunks(data, chunk=0 if len(query.arguments) == 2 else int(query.arguments[2]))
    for i, answer in enumerate(chunk):
        assert i < 127
        data = base64encode(chr(i).encode() + answer)
        response.add_answer(query, data, qtype=query.available_qtype.TXT)
    if len(query.arguments) == 2:
        chunks = estimate_chunks(data)
        response.add_answer(query, int_to_ipv6(chunks), qtype=query.available_qtype.AAAA)
    return response


if __name__ == '__main__':
    from dnschaind.services.bitcoin import INSTANCE as bitcoind
    b = bitcoind.getblock('000000000000000000a2a646ca401d78627db077a28817fa22adb91cc357c8cc')
    t = b['tx']
    res = get_merkle_proof('ff39f5ddfefdbd01056ee09d5629d04c53480eb32f9034f655948fd6b0912e14', t)
    hexroot = '592850c4a8737f3f1be76c1384b3ebd753caa5622e1de21463fc56e11a8ec912'
    res = check_merkle_proof(res, hexroot)

    import base64
    a = base64.b64decode('ABQukbDWj5RV9jSQL7MOSFNM0ClWneBuBQG9/f7d9Tn/AHM7TcHq3FwY/R/UHTbN3OYzpQZoCYQFjA3VjiZkbjd8AbPUa2e1eyMvg3JZh/128AZvLzj910tlaT+/64mx2w==')
    b = base64.b64decode('AYH9Afx1EO7TX+nQk3t7LnE1LdYImVdO1JyGyLH3Txgo6Y1dAuWhKcn/alzRjFAiI8PnQFD2roXE16VfHCzQn1p7f4+TAY6dWKH+Qf77istXA4pldbiEPZ09zfY0DfVLqw==')
    c = base64.b64decode('As+d55/cAU64SlSTCVSJeodT4UfE795qnA+HPbXC44VD9XcKsSB7AfAoTCnUqJmNe8NPkHsfFUTv4qhfsotCRFhcWmjM3UbYARLpLxsHcIqK4YdgPwBQc3DWkvYDPZ+nbA==')
    d = base64.b64decode('ABWoeMM73Sy1AdU7dyRYsoC84A0K+don8J+pnM/FjOQwxBmbhK6A/mDYARfekuK3D8FXKR8Chao6hqpjDR2sOw2uYP4AnpHXDrwZAcoU9m1sHXuas0TET5zPODfcWGAsHg==')
    e = base64.b64decode('AT+ZTXYCGMPzZoh0AZ1V8P5xM0sD7appW3hethNY/dW6/8y4tHFrZlY25snvAQ==')
    assert a[0] == 0
    assert b[0] == 1
    assert c[0] == 2
    assert d[0] == 0
    assert e[0] == 1
    fromtxt = a[1:] + b[1:] + c[1:] + d[1:] + e[1:]
    check_merkle_proof(fromtxt, hexroot)
    print('Proof verified')
