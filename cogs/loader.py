from discord.ext import commands
import logging
from src.command_checks import only_owners


class Loader(commands.Cog):
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger

    @commands.command()
    @commands.check(only_owners)
    async def reload_mint_poster(self, ctx):
        try:
            self.bot.reload_extension("cogs.mint_poster")
        except Exception as e:
            await ctx.send(f"Error when trying to reload cog : {e}")
        else:
            await ctx.send(f"Cog mint_poster reloaded")

    @commands.command()
    @commands.check(only_owners)
    async def unload_mint_poster(self, ctx):
        try:
            self.bot.unload_extension("cogs.mint_poster")
        except Exception as e:
            await ctx.send(f"Error when trying to unload cog : {e}")
        else:
            await ctx.send(f"Cog mint_poster unloaded")

    @commands.command()
    @commands.check(only_owners)
    async def load_mint_poster(self, ctx):
        try:
            self.bot.load_extension("cogs.mint_poster")
        except Exception as e:
            await ctx.send(f"Error when trying to load cog : {e}")
        else:
            await ctx.send(f"Cog mint_poster loaded")
