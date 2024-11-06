from dotenv import load_dotenv
from phi.agent import Agent
# from phi.tools.googlesearch import GoogleSearch
# from phi.model.anthropic import Claude
from phi.model.openai import OpenAIChat
from phi.playground import Playground, serve_playground_app
from rich.prompt import Prompt
from prompt import *
from swap import *
import httpx
import typer
import json

load_dotenv()

def get_popular_nft(num: int = 5):
  """Use this function to get popular NFT.

  Args:
    num (str): Number of NFT to return. Defaults to 5.

  Returns:
    str: JSON string of NFT information.
  """
  resp = httpx.get(f'https://api-base.reservoir.tools/collections/trending/v1?limit={num}')
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

def buy_nft(name: str, contract: str):
  """Use this function to buy NFT.

  Args:
    name (str): Name of the NFT.
    contract (str): Contract address of the NFT.

  Returns:
    str: JSON string of magicLinks to buy the nft.
  """
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=buy-nft-okx'})

def donate(token: str, amount: str, recipient: str):
  """Use this function to send token to recipient.

  Args:
    token (str): Token symbol.
    amount (str): Amount of donation.
    recipient (str): Address to receive token.

  Returns:
    str: JSON string of magicLinks to send token.
  """
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=buy-me-a-coffee'})

def swap(token_from: str, token_to: str, amount: float):
  """Use this function to swap or buy one token from another token. Return error if given token is unsupported.

  Args:
    token_from (str): From token symbol.
    token_to (str): To token symbol.
    amount (str): Amount of ***token_from***.

  Returns:
    str: JSON string of magicLinks to swap token.
  """
  if token_from not in ERC20s:
    raise ValueError('token_from is not supported')
  if token_to not in ERC20s:
    raise ValueError('token_to is not supported')
  real_amount = int(amount * 10 ** ERC20s[token_from]['Decimals'])
  return json.dumps({'url': 'https://zklink.io/dashboard/intent?id=novaswap' + "?from=" + token_from + "&to=" + token_to + "&amount=" + str(real_amount)})

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
  tools = [get_popular_nft, buy_nft, donate, swap, mint_nft, send_red_packet,
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
  # print(buy_nft('Gemesis', '0xd0f6a80064580b685e71359277370d6d4eece3a4'))
  import sys
  if len(sys.argv) > 1 and sys.argv[1] == 's':
    serve_playground_app("main:app", host = '0.0.0.0')
  else:
    typer.run(terminal)
