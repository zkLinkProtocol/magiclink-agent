from dotenv import load_dotenv
from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
# from phi.model.anthropic import Claude
from phi.model.openai import OpenAIChat
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
import sys

load_dotenv()
okx = OKX()
debug_mode = False

def get_popular_nft(chain: str, num: int = 5):
  """Use this function to get popular NFT.

  Args:
    num (str): The number of NFT to return. Defaults to 5.
    chain (str): The blockchain where you buy NFT. Optional value can be Ethereum, Base, Arbitrum. Ask user if you don't know.

  Returns:
    str: JSON string of NFT information.
  """
  try:
    info = Chains[chain.lower()]
    resp = httpx.get(f'https://api{info["magiceden_alias"]}.reservoir.tools/collections/trending/v1?limit={num}')
    nft_info = resp.json()
    nfts = []
    for info in nft_info['collections']:
      floorAsk = info['floorAsk']
      floorPrice = floorAsk['price']['amount']['decimal']
      priceSymbol = floorAsk['price']['currency']['symbol']
      nfts.append({
        'name': info['name'],
        'price': f'{floorPrice} {priceSymbol}',
        'image': info['image'],
        'contract': info['id'],
      })
    return json.dumps(nfts)
  except:
    return json.dumps({"error": "Currently doesn't support {chain}"})

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
    return json.dumps({"error": "Failed to retrive price for {token}"})

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
    return json.dumps({"error": "Currently doesn't support {chain}"})

def send_token(token: str, amount: str, recipient: str, chain: str):
  """Use this function to send token to recipient. This function doesn't support buy tokens.

  Args:
    token (str): The symbol of token that you want to send.
    amount (str): The amount of token that you want to send. Ask user if you don't know.
    recipient (str): The address to receive token. Ask user if you don't know.
    chain (str): The blockchain where the transaction will happen. Optional value can be Ethereum, Optimism, Base, Arbitrum, zkLink, Linea, Manta, Scroll, BSC. Ask user if you don't know

  Returns:
    str: url string of magicLinks to send token.
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
    return f"https://magic.zklink.io/intent/{magicLinkCode['send']}/confirm?params={param}"
  except:
    return json.dumps({"error": f"Currently don't support send {token} on {chain}"})

def swap(token_from: str, token_to: str, amount_from: str, chain: str):
  """Use this function to swap or buy one ERC20 token from another ERC20 token. This function doesn't support cross-chain swap. If user specify source chain and destination chain,
  we should not use this function.
  This function doesn't support set `amount_to` (amount of token_to). This method does not support setting amount_to. If the user gives amount_to, please inform them that this function does not support it
  This function only support swap between ERC20 token or ETH. BTC, BNB, etc are not supported.

  Args:
    token_from (str): The symbol of ERC20 token that you want to swap. Ask user if you don't know.
    token_to (str): The symbol of ERC20 token that you want to swap for.
    amount_from (str): The amount of token (token_from) that you want to swap. Ask user if you don't know.
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
    return f"https://magic.zklink.io/intent/{magicLinkCode['swap']}/confirm?params={param}"
  except:
    return json.dumps({"error": f"Currently don't support swap {token_from} and {token_to} on {chain}"})

chatbot = Agent(
  agent_id = 'magicLinkAgent',
  model = OpenAIChat(id = 'gpt-4o-mini', temperature = 0.0),
  # model = Claude(id = 'claude-3-haiku-20240307'),
  add_history_to_messages = True,
  num_history_responses = 5,
  system_prompt = system_prompt,
  markdown = False,
  tools = [get_popular_nft, get_wallet_balance, send_token, swap, get_token_price, DuckDuckGo()],
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

app = Playground(agents=[chatbot, twitter_bot]).get_app()

if __name__ == "__main__":
  # print(get_popular_nft(1))
  # print(send_token('usdc', 100, '0x1234567890123456789012345678901234567890', 'arbitrum'))
  # print(swap('usdc', 'eth', 1000, 'arb'))
  # print(get_token_price('sol'))

  if len(sys.argv) > 1 and sys.argv[1] == 's':
    serve_playground_app("main:app", host = '0.0.0.0')
  else:
    typer.run(terminal)
