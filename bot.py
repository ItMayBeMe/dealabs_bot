import discord
from discord.ext import commands
from dealabs import Dealabs
import json
dealabs = Dealabs()
import time
import asyncio
config = json.loads(open('./config.json').read())
import traceback
from notifier import Notifier
import sys
from collections import defaultdict


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notifiers = defaultdict(list)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        for chan, conf in config.get('channels').items():
            notifier = Notifier(self.get_channel(int(chan)), conf)
            categories = conf.get("categories") if len(conf.get("categories")) > 0 else ["High-Tech", "Consoles & jeux vidéo", "Épicerie & courses", "Mode & accessoires", "Sports & plein air", "Voyages", "Culture & divertissement", "Santé & Cosmétiques", "Famille & enfants", "Maison & Habitat", "Jardin & bricolage", "Auto-Moto", "Finances & Assurances", "Forfaits mobiles et internet", "Services"]
            for categorie in categories:
                self.notifiers['{0}:{1}'.format(conf.get("type"), categorie)].append(notifier)
        print(self.notifiers)

    async def my_background_task(self):
        try:
            await self.wait_until_ready()
            counter = 0
            last_link = ""
            found = False
            while not self.is_closed():
                print("new search")
                deals = dealabs.get_new_deals()
                for deal in deals["data"][:1]:
                    if not found:
                        if deal["deal_uri"] != last_link:
                            print("New Deal + " + deal["deal_uri"])
                            deal_key = 'new:{0}'.format(deal['group_display_summary'])
                            for key, notifiers in self.notifiers.items():
                                if deal_key == key:
                                    for notifier in notifiers:
                                        if notifier.match_keywords(deal):
                                            await notifier.channel.send(deal["deal_uri"])
                        else: 
                            found = True
                last_link = deals["data"][0]["deal_uri"]
                found = False
                await asyncio.sleep(10)
        except Exception:
            traceback.print_exc()

    async def send_deal(self, channel, deal):
        await channel.send(deal["deal_uri"])

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