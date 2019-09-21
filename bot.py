import discord
from discord.ext import commands
from dealabs import Dealabs
import json
import time
import asyncio
import traceback
from notifier import Notifier
import sys
import os
from collections import defaultdict
from collections import deque
import logging

config = json.loads(open('./config.json').read())

LOG_LEVEL = getattr(logging, config.get("LOG_LEVEL"), None)
if not isinstance(LOG_LEVEL, int):
    print(f"ERROR: invalid LOG_LEVEL: {config.get('LOG_LEVEL')}")
    sys.exit(1)
if not os.path.isdir("./logs"):
    os.makedirs("./logs")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s.%(msecs)03d][%(levelname)s][%(module)s - %(funcName)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(f"./logs/dealabs_bot-{time.time()}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


class DealabsCog(commands.Cog):
    def __init__(self, _bot: discord.ext.commands.Bot):
        self.bot: discord.ext.commands.Bot = _bot
        self.notifiers = defaultdict(list)
        self.already_sent_new = deque(maxlen=400)
        # create the background task and run it in the background
        self.bg_task = bot.loop.create_task(self.my_background_task())

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Logged in as: {0} ({1})".format(
            self.bot.user.name, self.bot.user.id
        ))
        for chan, conf in config.get('channels').items():
            notifier = Notifier(self.bot.get_channel(int(chan)), conf)
            categories = conf.get("categories") if len(conf.get("categories")) > 0 else ["High-Tech", "Consoles & jeux vidéo", "Épicerie & courses", "Mode & accessoires", "Sports & plein air", "Voyages", "Culture & divertissement", "Santé & Cosmétiques", "Famille & enfants", "Maison & Habitat", "Jardin & bricolage", "Auto-Moto", "Finances & Assurances", "Forfaits mobiles et internet", "Services"]
            for categorie in categories:
                self.notifiers['{0}:{1}'.format(conf.get("type"), categorie)].append(notifier)
        logging.debug(f"notifiers: {self.notifiers}")

    @commands.command()
    async def search(self, ctx, *, query: str):
        keyword = query
        deals = dealabs.search_deals(
            params={
                "order_by": "hot",
                "query": keyword
            }
        )
        embed = discord.Embed(title=f"Search - {keyword}", color=0x00ff00)
        for deal in deals["data"]:
            embed.add_field(
                name=f"[{deal['title']}]",
                value=":euro: {}€ - {}:fire: - [Lien]({})".format(
                    deal.get("price", "Unknown"),
                    deal['temperature_rating'],
                    deal['deal_uri']
                ),
                inline=False
            )
        await ctx.send(embed=embed)

    async def my_background_task(self):
        try:
            await self.bot.wait_until_ready()
            while not self.bot.is_closed():
                logging.debug("new search")
                deals = dealabs.get_new_deals()
                for deal in deals["data"][:1]:
                    if deal['thread_id'] not in self.already_sent_new:
                        logging.info(f"new deal: {deal['deal_uri']}")
                        deal_key = 'new:{0}'.format(deal['group_display_summary'])
                        for key, notifiers in self.notifiers.items():
                            if deal_key == key:
                                for notifier in notifiers:
                                    if notifier.match_keywords(deal):
                                        await notifier.channel.send(deal["deal_uri"])
                        self.already_sent_new.append(deal['thread_id'])
                await asyncio.sleep(10)
        except Exception:
            traceback.print_exc()

    async def send_deal(self, channel, deal):
        await channel.send(deal["deal_uri"])


dealabs = Dealabs()
bot = commands.Bot(
    command_prefix=config.get('BOT_PREFIX')
)
bot.add_cog(DealabsCog(bot))

bot.run(config.get('BOT_TOKEN'))
