from discord.ext import commands
from src.utils import GcpUtils
import os
from cogs.loader import Loader
from src.logger import create_logger


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-creds.json"
    discord_secret_resource_id = "projects/148433842428/secrets/mint-poster-discord-token/versions/1"
    discord_secret = GcpUtils.get_json_dict_from_secret_resource_id(discord_secret_resource_id)
    discord_token = discord_secret["api_key"]
    print(discord_token)
    logger = create_logger()
    mint_poster_bot = commands.Bot(command_prefix="!")
    mint_poster_bot.add_cog(Loader(bot=mint_poster_bot, logger=logger))
    print('succeeded logging in')
    mint_poster_bot.run(discord_token)

if __name__=="__main__":
    main()
