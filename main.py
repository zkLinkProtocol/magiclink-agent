from dotenv import load_dotenv
from phi.agent import Agent
# from phi.tools.googlesearch import GoogleSearch
# from phi.model.anthropic import Claude
from phi.model.openai import OpenAIChat
from phi.playground import Playground, serve_playground_app
from rich.prompt import Prompt
from constants import *
from okx import OKX
from prompt import *
import httpx
import typer
import json
import os
import sys
from urllib.parse import quote

load_dotenv()
okx = OKX()
debug_mode = False

def get_popular_nft(chain: str, num: int = 5):
  """Use this function to get popular NFT.

  Args:
    num (str): Number of NFT to return. Defaults to 5.
    chain (str): Blockchain name. Optional value can be Ethereum, Base, Arbitrum. Ask user if you don't know

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

def send_token(token: str, amount: str, recipient: str, chain: str):
  """Use this function to send token to recipient.

  Args:
    token (str): Token symbol.
    amount (str): Amount of donation.
    recipient (str): Address to receive token.
    chain (str): Blockchain name. Optional value can be Ethereum, Optimism, Base, Arbitrum, zkLink, Linea, Manta, Scroll, BSC. Ask user if you don't know

  Returns:
    str: JSON string of magicLinks to send token.
  """
  try:
    info = Chains[chain.lower()]
    if 'send' not in info['action']:
      raise Exception(f'Send action currently unavailable on {chain}')
    chainId = info['id']
    tokenAddress = info['token'][token.upper()]
    param = quote(json.dumps({
      "chainId": chainId,
      "params": {
        "token": tokenAddress,
        "value": amount,
        "recipient": recipient,
      }
    }, separators=(',', ':')))
    return json.dumps({'url': f"https://magic.zklink.io/intent/{magicLinkCode['send']}/confirm?params={param}"})
  except:
    return json.dumps({"error": f"Currently don't support send {token} on {chain}"})

def swap(token_from: str, token_to: str, amount: str, chain: str):
  """Use this function to swap or buy one token from another token.

  Args:
    token_from (str): The symbol of token that you want to swap.
    token_to (str): The symbol of token that you want to swap for.
    amount (str): The amount of token that you want to swap (**token_from**).
    chain (str): The blockchain where the swap will happen. Optional value can be Ethereum, Optimism, Base, Arbitrum. Ask user if you don't know

  Returns:
    str: JSON string of magicLinks to swap token.
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
    if token_to.upper() in info['token']:
      toAddress = info['token'][token_to.upper()]
    else:
      toAddress = okxInfo[token_to.upper()]['address']
    param = quote(json.dumps({
      "chainId": chainId,
      "params": {
        "amountToBuy": amount,
        "tokenFrom": fromAddress,
        "tokenTo": toAddress,
      }
    }, separators=(',', ':')))
    return json.dumps({'url': f"https://magic.zklink.io/intent/{magicLinkCode['swap']}/confirm?params={param}"})
  except:
    return json.dumps({"error": f"Currently don't support swap {token_from} and {token_to} on {chain}"})

chatbot = Agent(
  agent_id = 'magicLinkAgent',
  model = OpenAIChat(id = 'gpt-4o-mini'),
  # model = Claude(id = 'claude-3-haiku-20240307'),
  add_history_to_messages = True,
  system_prompt = system_prompt,
  tools = [get_popular_nft, send_token, swap],
  use_tools = True,
  show_tool_calls = True,
  debug_mode = os.getenv("AGENT_DEBUG", "false") == 'true',
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

app = Playground(agents=[chatbot]).get_app()

if __name__ == "__main__":
  # print(get_popular_nft(1))
  # print(send_token('usdc', 100, '0x1234567890123456789012345678901234567890', 'arbitrum'))
  # print(swap('usdc', 'eth', 100, 'op'))
  if len(sys.argv) > 1 and sys.argv[1] == 's':
    serve_playground_app("main:app", host = '0.0.0.0')
  else:
    typer.run(terminal)
