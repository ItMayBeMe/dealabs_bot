import discord
from discord.ext import commands
from dealabs import Dealabs
import json
dealabs = Dealabs()

config = json.loads(open('./config.json').read())
bot = commands.Bot(command_prefix="?")

# Bot functions
@bot.event
async def on_ready():
    print("Everything's all ready to go~")

@bot.command()
async def search(ctx, *, query:str):
    print("Search:", query)
    deals = dealabs.search_deals(
        params={
            "order_by": "hot",
            "query": query
        }
    )
    embed = discord.Embed(title=f"Search - {query}", color=0x00ff00)
    for deal in deals["data"]:
        embed.add_field(
            name=f"[{deal['title']}]", 
            value=f":euro: {deal['price']}€ - {deal['temperature_rating']}:fire: - [Lien]({deal['deal_uri']})", 
            inline=False
        )
    await ctx.send(embed=embed)

bot.run(config.get('BOT_TOKEN'))