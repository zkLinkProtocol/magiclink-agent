Chains = {
  'ethereum': {
    'id': 1,
    'action': ['send', 'swap', 'nft', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
      'USDC': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      'WETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    },
    'magiceden_alias': '',
    'okx_alias': 'Ethereum',
  },
  'optimism': {
    'id': 10,
    'action': ['send', 'swap', 'nft', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
      'USDC': '0x0b2c639c533813f4aa9d7837caf62653d097ff85',
      'WETH': '0x4200000000000000000000000000000000000006',
    },
    'magiceden_alias': '-optimism',
    'okx_alias': 'Optimism',
  },
  'base': {
    'id': 8453,
    'action': ['send', 'swap', 'nft', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDC': '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
      'WETH': '0x4200000000000000000000000000000000000006',
    },
    'magiceden_alias': '-base',
    'okx_alias': 'Base',
  },
  'arbitrum': {
    'id': 42161,
    'action': ['send', 'swap', 'nft', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
      'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
      'WETH': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
    },
    'magiceden_alias': '-arbitrum',
    'okx_alias': 'Arbitrum',
  },
  'nova': {
    'id': 810180,
    'action': ['send'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0x2F8A25ac62179B31D62D7F80884AE57464699059',
      'USDC': '0x1a1A3b2ff016332e866787B311fcB63928464509',
    },
  },
  'linea': {
    'id': 59144,
    'action': ['send', 'nft', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0xa219439258ca9da29e9cc4ce5596924745e12b93',
      'USDC': '0x176211869ca2b568f2a7d4ee941e073a821ee1ff',
      'WETH': '0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f',
    },
    'magiceden_alias': '-linea',
  },
  'manta': {
    'id': 169,
    'action': ['send', 'bridge'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
      'USDT': '0xf417f5a458ec102b90352f697d6e2ac3a3d2851f',
      'USDC': '0xb73603c5d87fa094b7314c74ace2e64d165016fb',
      'WETH': '0x0dc808adce2099a9f62aa87d9670745aba741746',
    },
  },
  'scroll': {
    'id': 534352,
    'action': ['send', 'nft'],
    'token': {
      'ETH': '0x0000000000000000000000000000000000000000',
    },
    'magiceden_alias': '-scroll',
  },
  'zksync': {
    'id': 324,
    'action': ['nft'],
    'magiceden_alias': '-zksync',
  },
  'bsc': {
    'id': 56,
    'action': ['send', 'nft', 'bridge'],
    'token': {
      'BNB': '0x0000000000000000000000000000000000000000',
      'ETH': '0x2170ed0880ac9a755fd29b2688956bd959f933f8',
      'USDT': '0x55d398326f99059ff775485246999027b3197955',
      'USDC': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
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
  'binance': Chains['bsc'],
})

magicLinkCode = {
  'send': 'WqL5jFAm',
  'swap': '1se4O1TV',
  'nft': 'rD7pPx8q',
  'dxfun': 'wpgDP6DU',
  'bridge': 'ordsAnio',
}
