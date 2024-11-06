from dotenv import load_dotenv
from phi.agent import Agent
# from phi.tools.googlesearch import GoogleSearch
# from phi.model.anthropic import Claude
from phi.model.openai import OpenAIChat
from phi.playground import Playground, serve_playground_app
from rich.prompt import Prompt
from constants import *
from prompt import *
import httpx
import typer
import json
from urllib.parse import quote

load_dotenv()

def get_popular_nft(num: int = 5, chain: str = 'Ethereum'):
  """Use this function to get popular NFT.

  Args:
    num (str): Number of NFT to return. Defaults to 5.

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
    return json.dumps({"error": "Failed to get NFT detail through Magic Eden"})

def buy_nft(name: str, contract: str):
  """Use this function to buy NFT.

  Args:
    name (str): Name of the NFT.
    contract (str): Contract address of the NFT.

  Returns:
    str: JSON string of magicLinks to buy the nft.
  """
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=buy-nft-okx'})

def send_token(token: str, amount: str, recipient: str, chain: str = 'Ethereum'):
  """Use this function to send token to recipient.

  Args:
    token (str): Token symbol.
    amount (str): Amount of donation.
    recipient (str): Address to receive token.
    chain (str): Blockchain name. Defaults to Ethereum.

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
    return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=buy-me-a-coffee'})

def swap(token_from: str, token_to: str, amount: str, chain: str = 'Ethereum'):
  """Use this function to swap or buy one token from another token

  Args:
    token_from (str): From token symbol.
    token_to (str): To token symbol.
    amount (str): Amount of ***token_from***.

  Returns:
    str: JSON string of magicLinks to swap token.
  """
  try:
    info = Chains[chain.lower()]
    if 'swap' not in info['action']:
      raise Exception(f'Swap action currently unavailable on {chain}')
    chainId = info['id']
    fromAddress = info['token'][token_from.upper()]
    toAddress = info['token'][token_to.upper()]
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
    return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=magic-swap'})

def mint_nft(nft_name: str, quantity: int, recipient: str):
  """Use this function to mint NFT.

  Args:
    nft_name (str): NFT name.
    quantity (str): Number of NFTs to be minted.
    recipient (str): Address to receive NFT.

  Returns:
    str: JSON string of magicLinks to mint NFT.
  """
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=mint-nft'})

def send_red_packet(token: str, number: int, total_amount: str):
  """Use this function to send red packet.

  Args:
    token (str): Token symbol.
    number (str): Number of red packets.
    total_amount (str): Amount of distributed token.

  Returns:
    str: JSON string of magicLinks to send red packet.
  """
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=red-envelope'})

chatbot = Agent(
  agent_id = 'magicLinkAgent',
  model = OpenAIChat(id = 'gpt-4o-mini'),
  # model = Claude(id = 'claude-3-haiku-20240307'),
  add_history_to_messages = True,
  system_prompt = system_prompt,
  tools = [get_popular_nft, buy_nft, send_token, swap, mint_nft, send_red_packet,
          #  GoogleSearch()
           ],
  use_tools = True,
  show_tool_calls = True,
  debug_mode = False,
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
  # print(swap('usdc', 'eth', 100, 'arbitrum'))
  import sys
  if len(sys.argv) > 1 and sys.argv[1] == 's':
    serve_playground_app("main:app", host = '0.0.0.0')
  else:
    typer.run(terminal)
