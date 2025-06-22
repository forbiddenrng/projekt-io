from twikit import Client, TooManyRequests
from configparser import ConfigParser
import asyncio
#* login credentials
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']


async def login():
  client = Client(language='pl')
  await client.login(auth_info_1=username, auth_info_2=email, password=password)
  client.save_cookies('cookies.json')


async def logout():
  client = Client(language='pl')
  client.load_cookies('cookies.json')
  await client.logout()

asyncio.run(login())
# asyncio.run(logout())