from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from rich.prompt import Prompt
from prompt import system_prompt, nft_prompt
import httpx
import typer

import json
import os

load_dotenv()

def get_popular_nft(num: int = 5):
  """Use this function to get popular NFT.

  Args:
    num (int): Number of NFT to return. Defaults to 5.

  Returns:
    str: JSON string of NFT infomation.
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
  post_body = nft_prompt % (name, contract)
  headers = {
    'Content-Type': 'application/json',
    'Authorization': os.environ['ACTION_TOKEN']
  }
  resp = httpx.post('https://api-intent.sepolia.zklink.io/api/action-url', content = post_body, headers = headers)
  info = resp.json()
  magic_link_url = f'https://magic-test.zklink.io/intent/{info["data"]}'
  print(f'已为您创建购买{name}的magicLink：{magic_link_url}')
  return json.dumps({'url': magic_link_url})

def chatbot():
  session_id = None
  agent = Agent(
    model = OpenAIChat(id='gpt-4o-mini'),
    add_history_to_messages = True,
    system_prompt = system_prompt,
    tools = [get_popular_nft, buy_nft],
    use_tools = True,
    show_tool_calls = True,
    debug_mode = True,
  )
  if session_id is None:
    session_id = agent.session_id
    print(f"Started Run: {session_id}\n")
  else:
    print(f"Continuing Run: {session_id}\n")
  while True:
    message = Prompt.ask(f"[bold] :sunglasses: user [/bold]")
    if message in ("exit", "bye"):
      break
    agent.print_response(message)

if __name__ == "__main__":
  # print(get_popular_nft(1))
  # print(buy_nft('Gemesis', '0xd0f6a80064580b685e71359277370d6d4eece3a4'))
  typer.run(chatbot)
