from constants import *
from okx import OKX
import json

okx = OKX()
tokens = {}
for chain in Chains.values():
  if 'swap' in chain['action']:
    tokens[chain['okx_alias']] = {}
    info = okx.req('GET', f"/api/v5/dex/aggregator/all-tokens?chainId={chain['id']}")
    for token in info['data']:
      tokens[chain['okx_alias']][token['tokenSymbol'].upper()] = {
        'address': token['tokenContractAddress'],
        'logo': token['tokenLogoUrl'],
        'decimals': token['decimals'],
      }
with open('okx_swap.json', 'w') as f:
  json.dump(tokens, f)
