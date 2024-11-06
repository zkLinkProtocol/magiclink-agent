Chains = {
  'ethereum': {
    'id': 1,
    'action': ['send', 'swap'],
    'token': {
      'ETH': '',
    },
    'magiceden_alias': '',
  },
  'optimism': {
    'id': 10,
    'action': ['send', 'swap'],
    'token': {
      'ETH': '',
    },
  },
  'base': {
    'id': 8453,
    'action': ['send', 'swap'],
    'token': {
      'ETH': '',
    },
    'magiceden_alias': '-base',
  },
  'arbitrum': {
    'id': 42161,
    'action': ['send', 'swap'],
    'token': {
      'ETH': '',
      'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
      'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    },
    'magiceden_alias': '-arbitrum',
  },
  'nova': {
    'id': 810180,
    'action': ['send'],
    'token': {
      'ETH': '',
      'USDT': '0x2F8A25ac62179B31D62D7F80884AE57464699059',
      'USDC': '0x1a1A3b2ff016332e866787B311fcB63928464509',
    },
  },
  'linea': {
    'id': 59144,
    'action': ['send'],
    'token': {
      'ETH': '',
    },
    'magiceden_alias': '-linea',
  },
  'manta': {
    'id': 169,
    'action': ['send'],
    'token': {
      'ETH': '',
    },
  },
  'scroll': {
    'id': 534352,
    'action': ['send'],
    'token': {
      'ETH': '',
    },
    'magiceden_alias': '-scroll',
  },
  'zksync': {
    'id': 324,
    'action': ['send'],
    'magiceden_alias': '-zksync',
  },
  'mantle': {
    'id': 5000,
    'action': ['send'],
  },
  'bsc': {
    'id': 56,
    'action': ['send'],
    'token': {
      'BNB': '',
    },
    'magiceden_alias': '-bsc',
  },
}

# chain alias
Chains.update({
  'zklink': Chains['nova'],
  'op': Chains['optimism'],
  'arb': Chains['arbitrum'],
  'arbi': Chains['arbitrum'],
  'bnb': Chains['bsc'],
})

magicLinkCode = {
  'send': 'WqL5jFAm',
  'swap': '1se4O1TV',
}
