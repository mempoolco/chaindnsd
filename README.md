# dnschaind

A DNS with Bitcoin Blockchain resolution for full SPV over UDP DNS

Complete unstable, use weird conventions and checksums to route data over 
CNAME, TXT e AAAA records. 


#### Requirements

- Python 3.5
- Bitcoind full node
- A domain name

#### Features

- Get blockhash by height
- Get blockheaders by hash
- Get merkleproof (w.i.p.)
- Push tx (todo)
- Verify unspent (todo)

## Setup

Clone and build local environment
```buildoutcfg

$ git clone https://github.com/dnschain/dnschaind.git
$ cd dnschaind
$ ./localenv.sh

```

Edit dnschaind/dnschain/settings.py with your favorite editor, and change
bitcoinrpc credentials to connect to your bitcoind. No SSL support available. 
If you're going on the internet with rpc, use an SSH tunnel.

Change the following:
```buildoutcfg

BITCOIND_USER = b'rpcuser'
BITCOIND_PASS = b'passw0rd'
BITCOIND_HOSTNAME = b'http://bitcoin_node:8332'

```
 
At this point, to test dnschaind in a local environment is not mandatory to 
have a real domain name. 


#### Local usage for testing:

```buildoutcfg
$ venv/bin/python dnschaind.py

```
And no more! Run dnschaind, as you have seen in settings.py, dnschaind will bind to localhost:8053 

## Using dnschain

#### get block hash
Try with the genesis block:

```
$ dig 0.blockhash.btc.domain.co AAAA @localhost -p 8053
```
And pay attention to the answer section:
```
;; ANSWER SECTION:
0.blockhash.btc.domain.co. 31449600 IN AAAA 1000:19:d668:9c08:5ae1:6583:1e93:4ff7
0.blockhash.btc.domain.co. 31449600 IN AAAA 1001:63ae:46a2:a6c1:72b3:f1b6:a8c:e26f

```
The block hash is stripped of the 8 leading zeros required since the genesis block, and encoded
in two ipv6 addresses, hopefully this query will be cached for 31449600 seconds, if the block is old enough.
To avoid orphans caching, TTL is set to 0 for blocks with <6 confirmations.

The data over ipv6 encoding works as follow. 14 bytes are encoded on each IP

Read the first ip: 

- 10 is the loopback interface prefix
- 00 is the data chunk index

All after the network prefix is data, ipv6 addresses are 0-padded, so, the blockhash is:

```
00000000 + 00 19d6689c085ae165831e934ff7 + 63ae46a2a6c172b3f1b6 + 0 + a8ce26f
```

Added leading zeros, padding, data from the first ip, data from the second, padding, more data from the second ip,
an you can bet this is the genesis block:

```
000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f
```

#### get block header

Block headers are served as TXT records.
 
You can also check, with the block header API, at which height
of the blockchain this block is, with the int over ipv6 encoding.

Again, remove the 8 leading zeros from the blockhash (63 chars hosts limit).

```
$ dig 0019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f.blockheader.btc.domain.com AAAA @localhost -p 8053 

```

The answer is the header, with 2 checksum bytes appended, base64 encoded.

```
0019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f.blockheader.btc. 31449600 IN TXT 
"AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OIilEyOp+4qkse
Xkopq19J//8AHR2sK3yvQg=="

```

You can use Python to decode and check the block header:

```
Python 3.5.2 (default, Jun  6 2017, 19:18:05) 
[GCC 4.9.2] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import base64
>>> import binascii
>>> import hashlib 
>>> header = "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO6Pt/Xp7ErJ6xyw+Z3aPYX/IG8OIilEyOp+4qkseXkopq19J//8AHR2sK3yvQg=="
>>> base64.b64decode(header)  
b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\xa3\xed\xfdz{\x12\xb2z\xc7,>gv\x8fa\x7f\xc8\x1b\xc3\x88\x8aQ2:\x9f\xb8\xaaK\x1e^J)\xab_I\xff\xff\x00\x1d\x1d\xac+|\xafB'
>>> header_bytes = base64.b64decode(header)
```
checksum:
```
>>> assert hashlib.sha256(header_bytes[:-2]).digest()[:2] == header_bytes[-2:])
```
back from block headers to blockhash
```
>>> binascii.hexlify(hashlib.sha256(hashlib.sha256(header_bytes[:-2]).digest()).digest()[::-1])
b'000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f' 


```

The meaning of the block header is out of scope of the readme, if you are in doubt you may want to read more about how
the bitcoin blockchain works. 

In addition with the headers, the blockheight (if available) is returned with AAAA records:

```buildoutcfg
$ dig 0019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f.blockheader.btc.domain.co AAAA @localhost -p 8053
```

In the int over AAAA encoding, 1000 is the data prefix (without indexes), and the remaining part of the IP
is the integer.

This is 0, the genesis block:

```buildoutcfg
0019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f.blockheader.btc.domain.co. 
31449600 IN AAAA 1000::
```

This is, for example, the record for the block 400002 
```buildoutcfg
1000::040:0002
```


#### get merkle proof

The merkle proof API make you able to verify independently if a transaction is the blockchain.

Actually this requires a little work to mantain updated a blocks checkpoints list, is not mandatory, but helps, as in 
any SPV protocol: the more checkpoints you have, the less bandwidth you need.

The merkle proof API gives you the branches of the merkle tree you need to verify the provided transaction, if it's 
actually in the blockchain.

```buildoutcfg
$ dig 593dd7c0ec799d9e11ac514bf2b445d4.437d6ca3ef58e617095590b9b662d649.merkleproof.btc.domain.co
 
```

```
TODO
```


