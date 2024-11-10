from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.playground import Playground, serve_playground_app
from phi.storage.agent.sqlite import SqlAgentStorage
from rich.prompt import Prompt
from constants import *
from okx import OKX
from prompt import *
import httpx
import typer
import base64
import json
import os
import random
import sys

load_dotenv()
okx = OKX()
debug_mode = False

def get_popular_nft(chain: str, num: int = 5):
  """Use this function to get popular NFT.

  Args:
    num (str): The number of NFT to return. Defaults to 5.
    chain (str): The blockchain where you buy NFT. Optional value can be Ethereum, Base, Optimism, Arbitrum, BSC, Linea, Scroll, Ask user if you don't know.

  Returns:
    str: JSON string of NFT information.
  """
  try:
    info = Chains[chain.lower()]
    resp = httpx.get(f'https://api{info["magiceden_alias"]}.reservoir.tools/collections/trending/v1?limit={num}')
    nft_info = resp.json()
    nfts = []
    for info in nft_info['collections']:
      try:
        floorAsk = info['floorAsk']
        floorPrice = floorAsk['price']['amount']['decimal']
        priceSymbol = floorAsk['price']['currency']['symbol']
      except:
        continue
      nfts.append({
        'name': info['name'],
        'price': f'{floorPrice} {priceSymbol}',
        'image': info['image'],
        'contract': info['id'],
      })
    return json.dumps(nfts)
  except:
    return json.dumps({"error": f"Currently doesn't support {chain}"})

def get_nft_info(chain: str, name: str):
  """Use this function to get NFT information such as contract address, and price.

  Args:
    chain (str): The blockchain where you buy NFT. Optional value can be Ethereum, Base, Optimism, Arbitrum, BSC, Linea, Scroll. Ask user if you don't know.
    name (str): The nft name where you buy NFT. Ask user if you don't know.

  Returns:
    str: JSON string of NFT information.
  """
  try:
    info = Chains[chain.lower()]
    resp = httpx.get(f'https://api{info["magiceden_alias"]}.reservoir.tools/collections/v7?limit=7&sortBy=7DayVolume&name={name}')
    nft_info = resp.json()
    nfts = []
    for info in nft_info['collections']:
      try:
        floorAsk = info['floorAsk']
        floorPrice = floorAsk['price']['amount']['decimal']
        priceSymbol = floorAsk['price']['currency']['symbol']
      except:
        continue
      nfts.append({
        'name': info['name'],
        'price': f'{floorPrice} {priceSymbol}',
        'image': info['image'],
        'contract': info['id'],
      })
    return json.dumps(nfts)
  except:
    return json.dumps({"error": f"Currently doesn't support {chain}"})

def buy_nft(chain: str, address: str, quantity: int = 1):
  """Use this function to generate links to buy NFT.

  Args:
    chain (str): The blockchain where you buy NFT. Optional value can be Ethereum, Base, Optimism, Arbitrum, BSC, Linea, Scroll. Ask user if you don't know.
    address (str): The NFT address.
    quantity (int): Number of NFT to buy. Defaults to 1.

  Returns:
    str: url string of magicLinks to buy nft.
  """
  try:
    info = Chains[chain.lower()]
    if 'nft' not in info['action']:
      raise Exception(f'Buy NFT currently unavailable on {chain}')
    chainId = info['id']
    param = base64.urlsafe_b64encode(json.dumps({
      "chainId": chainId,
      "params": {
        "queryType": 'contract',
        "queryValue": address,
        "quantity": str(quantity),
      }
    }, separators=(',', ':')).encode()).decode()
    return json.dumps({
      'magicLink': f"https://magic.zklink.io/intent/{magicLinkCode['nft']}/confirm?params={param}",
      'tip_url': f"https://magic.zklink.io/intent/{random.choice(info['tip_code'])}",
    })
  except:
    return json.dumps({"error": f"Failed to generate transaction to buy NFT"})

def get_popular_token():
  """Use this function to get popular token. Also introduce their popular reason.

  Returns:
    str: JSON string of token information.
  """
  try:
    trend_resp = httpx.get('https://api.coingecko.com/api/v3/search/trending')
    trend = trend_resp.json()
    categories = random.sample(trend['categories'], 3)
    result = []
    for i in range(0, 3):
      coin_resp = httpx.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&page=1&per_page=10&category={categories[i]['slug']}")
      coins = coin_resp.json()
      choosing_coins = random.sample(coins, 3)
      coin = []
      for j in range(0, 3):
        coin.append({
          'name': choosing_coins[j]['name'],
          'price': choosing_coins[j]['current_price'],
        })
      coin_trend = {
        'popular_reason': categories[i]['name'],
        'coin': coin
      }
      result.append(coin_trend)
    return json.dumps(result)
  except:
    return json.dumps({"error": "Failed to retrive token trend"})

def get_token_price(token: str):
  """Use this function to get real time token price.

  Args:
    token (str): The token you want to query.

  Returns:
    str: JSON string of token price.
  """
  try:
    return json.dumps(okx.req('GET', f"/api/v5/market/ticker?instId={token.upper()}-USDT"))
  except:
    return json.dumps({"error": f"Failed to retrive price for {token}"})

def get_wallet_balance(chain: str, wallet_address: str):
  """Use this function to get a list of token balance for specified chain.

  Args:
    chain (str): The blockchain where you want to query. Ask user if you don't know.
    wallet_address (str): The wallet address you want to query. Ask user if you don't know.

  Returns:
    str: JSON string of wallet balance.
  """
  try:
    info = Chains[chain.lower()]
    resp = okx.req('GET', f"/api/v5/wallet/asset/all-token-balances-by-address?address={wallet_address}&chains={str(info['id'])}")
    return json.dumps(resp)[:10000]
  except:
    return json.dumps({"error": f"Currently doesn't support {chain}"})

def send_token(token: str, amount: str, recipient: str, chain: str):
  """Use this function to send token to recipient. This function doesn't support buy tokens.

  Args:
    token (str): The symbol of token that you want to send.
    amount (str): The amount of token that you want to send. Ask user if you don't know.
    recipient (str): The address to receive token. Ask user if you don't know.
    chain (str): The blockchain where the transaction will happen. Optional value can be Ethereum, Optimism, Base, Arbitrum, zkLink, Linea, Manta, Scroll, BSC. Ask user if you don't know

  Returns:
    str: json string with magic link url to send token and tip_url.
  """
  try:
    info = Chains[chain.lower()]
    if 'send' not in info['action']:
      raise Exception(f'Send action currently unavailable on {chain}')
    chainId = info['id']
    tokenAddress = info['token'][token.upper()]
    param = base64.urlsafe_b64encode(json.dumps({
      "chainId": chainId,
      "params": {
        "token": tokenAddress,
        "value": amount,
        "recipient": recipient,
      }
    }, separators=(',', ':')).encode()).decode()
    return json.dumps({
      'magicLink': f"https://magic.zklink.io/intent/{magicLinkCode['send']}/confirm?params={param}",
      'tip_url': f"https://magic.zklink.io/intent/{random.choice(info['tip_code'])}",
    })
  except:
    return json.dumps({"error": f"Currently don't support send {token} on {chain}"})

def swap(token_from: str, token_to: str, amount_from: str, chain: str):
  """Use this function to swap or buy one ERC20 token from another ERC20 token on same chain. Call ***cross_chain*** instead if user tell you two different chains.
  This function doesn't support set `amount_to` (amount of token_to). If the user gives amount_to, please inform them that this function does not support specify target amount
  This function only support swap between ERC20 token or ETH. BTC, BNB, etc are not supported.

  Args:
    token_from (str): The symbol of ERC20 token that you want to swap. Ask user if you don't know.
    token_to (str): The symbol of ERC20 token that you want to swap for.
    amount_from (str): The amount of token (token_from) that you want to swap.
    chain (str): The blockchain where the swap will happen. Optional value can be Ethereum, Optimism, Base, Arbitrum. Ask user if you don't know.

  Returns:
    str: url string of magicLinks to swap token.
  """
  try:
    info = Chains[chain.lower()]
    if 'swap' not in info['action']:
      raise Exception()
    chainId = info['id']
    okxInfo = okx.TOKEN[info['okx_alias']]
    if token_from.upper() in info['token']:
      fromAddress = info['token'][token_from.upper()]
    else:
      fromAddress = okxInfo[token_from.upper()]['address']
    if fromAddress == '':
      fromAddress = '0x0000000000000000000000000000000000000000'
    if token_to.upper() in info['token']:
      toAddress = info['token'][token_to.upper()]
    else:
      toAddress = okxInfo[token_to.upper()]['address']
    if toAddress == '':
      toAddress = '0x0000000000000000000000000000000000000000'
    param = base64.urlsafe_b64encode(json.dumps({
      "chainId": chainId,
      "params": {
        "amountToBuy": amount_from,
        "tokenFrom": fromAddress,
        "tokenTo": toAddress,
      }
    }, separators=(',', ':')).encode()).decode()
    return json.dumps({
      'magicLink': f"https://magic.zklink.io/intent/{magicLinkCode['swap']}/confirm?params={param}",
      'tip_url': f"https://magic.zklink.io/intent/{random.choice(info['tip_code'])}",
    })
  except:
    return json.dumps({"error": f"Currently don't support swap {token_from} and {token_to} on {chain}"})

def create_coin(name: str, icon_url: str, description: str, symbol: str):
  """Use this function to create new meme coin. Inform user that currently you only support create coin on Base chain.

  Args:
    name (str): The full name of meme coin.
    icon_url (str): The icon image url of meme coin.
    description (str): The description of meme coin. Auto generate description if you don't know.
    symbol (str): The symbol of meme coin. Default value is as same as uppercase name. 

  Returns:
    str: url string of magicLinks to create meme coin.
  """
  if symbol == '':
    symbol = name
  symbol = name.upper().replace(' ', '')
  try:
    param = base64.urlsafe_b64encode(json.dumps({
      "chainId": 8453,
      "params": {
        "coinName": name,
        "coinSymbol": symbol,
        "coinIconUrl": icon_url,
        "coinDescription": description,
      }
    }, separators=(',', ':')).encode()).decode()
    return json.dumps({
      'magicLink': f"https://magic.zklink.io/intent/{magicLinkCode['dxfun']}/confirm?params={param}",
      'tip_url': f"https://magic.zklink.io/intent/{random.choice(Chains['base']['tip_code'])}",
    })
  except:
    return json.dumps({"error": f"Failed to generate transaction to create coin"})

def cross_chain(amount: str, chain_from: str, token_from: str, chain_to: str, token_to: str):
  """Use this function to bridge token between different networks.

  Args:
    amount (str): The amount of token that you want to cross chain. Ask user if you don't know.
    chain_from (str): The blockchain where you want to cross chain. Optional value can be Ethereum, Optimism, Base, Arbitrum, Linea, Manta, BSC. Ask user if you don't know.
    token_from (str): The token you want to cross chain. Optional value can be ETH, USDT, USDC, WETH, Ask user if you don't know.
    chain_to (str): The blockchain where you want to receive. Optional value can be Ethereum, Optimism, Base, Arbitrum, Linea, Manta, BSC. Ask user if you don't know.
    token_to (str): The token you want to receive. Ask user if you don't know.

  Returns:
    str: url string of magicLinks to cross chain.
  """
  try:
    info_from = Chains[chain_from.lower()]
    info_to = Chains[chain_to.lower()]
    if 'bridge' not in info_from['action'] or 'bridge' not in info_to['action']:
      raise Exception(f'Bridge action currently unavailable from {chain_from} to {chain_to}')
    chainIdFrom = info_from['id']
    chainIdTo = info_to['id']
    tokenAddressFrom = info_from['token'][token_from.upper()]
    tokenAddressTo = info_to['token'][token_to.upper()]
    param = base64.urlsafe_b64encode(json.dumps({
      "chainId": chainIdFrom,
      "params": {
        'bridgeAmount': amount,
        "tokenFrom": tokenAddressFrom,
        "toChainId": str(chainIdTo),
        "tokenTo": tokenAddressTo,
      }
    }, separators=(',', ':')).encode()).decode()
    return json.dumps({
      'magicLink': f"https://magic.zklink.io/intent/{magicLinkCode['bridge']}/confirm?params={param}",
      'tip_url': f"https://magic.zklink.io/intent/{random.choice(info_from['tip_code'])}",
    })
  except:
    return json.dumps({"error": f"Failed to generate transaction to cross chain"})

chatbot = Agent(
  agent_id = 'magicLinkAgent',
  model = OpenAIChat(id = 'gpt-4o-mini-2024-07-18', temperature = 0.0),
  add_history_to_messages = True,
  num_history_responses = 5,
  system_prompt = system_prompt,
  markdown = False,
  tools = [
    get_popular_token,
    get_wallet_balance,
    send_token,
    swap,
    get_token_price,
    get_nft_info,
    buy_nft,
    get_popular_nft,
    create_coin,
    cross_chain,
    DuckDuckGo(),
  ],
  use_tools = True,
  show_tool_calls = True,
  debug_mode = os.getenv("AGENT_DEBUG", "false") == 'true',
  storage = SqlAgentStorage(table_name="session", db_file="db/magicLink.db")
)

twitter_bot = chatbot.deep_copy(
  update = {
    'agent_id': 'twitter',
    'system_prompt': system_prompt + '\nYour reply should be no more than 250 characters.',
  }
)

debug_bot = chatbot.deep_copy(
  # from phi.model.anthropic import Claude
  # OpenAIChat(id = 'gpt-4o-2024-08-06')
  # Claude(id = 'claude-3-haiku-20240307')
  # Claude(id = 'claude-3-5-haiku-20241022')
  # Claude(id = 'claude-3-5-sonnet-20241022')
  update = {
    'agent_id': 'debug',
    'system_prompt': '',
    'model': OpenAIChat(id = 'gpt-4o-mini-2024-07-18', temperature = 0.0)
  }
)

def terminal():
  session_id = None
  if session_id is None:
    session_id = chatbot.session_id
    print(f"Started Run: {session_id}\n")
  else:
    print(f"Continuing Run: {session_id}\n")
  while True:
    message = Prompt.ask(f"[bold] :sunglasses: user [/bold]")
    if message in ("exit", "bye"):
      break
    chatbot.print_response(message)

app = Playground(agents=[chatbot, twitter_bot, debug_bot]).get_app()

if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == 's':
    serve_playground_app("main:app", host = '0.0.0.0')
  else:
    typer.run(terminal)
