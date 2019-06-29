import discord
from discord.ext import commands
from dealabs import Dealabs
import json
dealabs = Dealabs()
import time
import asyncio
config = json.loads(open('./config.json').read())
import traceback

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def my_background_task(self):
        try:
            await self.wait_until_ready()
            counter = 0
            channel = self.get_channel(593747695655452672) # channel ID goes here
            last_link = ""
            found = False
            while not self.is_closed():
                print("new search")
                deals = dealabs.get_new_deals()
                for deal in deals["data"]:
                    if last_link == "":
                        last_link = deals["data"][0]["deal_uri"]
                    if found == False:
                        if deal["deal_uri"] != last_link:
                            print("New Deal + " + deal["deal_uri"])
                            await channel.send(deal["deal_uri"])
                        else: 
                            found = True
                last_link = deals["data"][0]["deal_uri"]
                found = False
                await asyncio.sleep(10)
        except Exception:
            traceback.print_exc()

# @bot.command()
# async def search(ctx, *, query:str):
#     print("Search:", query)
#     deals = dealabs.search_deals(
#         params={
#             "order_by": "hot",
#             "query": query
#         }
#     )
#     embed = discord.Embed(title=f"Search - {query}", color=0x00ff00)
#     for deal in deals["data"]:
#         embed.add_field(
#             name=f"[{deal['title']}]", 
#             value=f":euro: {deal['price']}€ - {deal['temperature_rating']}:fire: - [Lien]({deal['deal_uri']})", 
#             inline=False
#         )
    # await ctx.send(embed=embed)

client = MyClient()
client.run(config.get('BOT_TOKEN'))