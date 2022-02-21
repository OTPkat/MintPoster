import discord
import typing
from discord.ext import tasks, commands
from src.command_checks import only_owners
import pandas as pd
from typing import Set
from google.cloud import bigquery
from google.cloud import storage
import json
from src.utils import GcpUtils

LOOP_TIME_POOL_MINT_DATA = 30
TABLE_ID = "spartan-theorem-328817.the_archive.mint_posts"
BUCKET_NAME = "archive-mint"


class MintPoster(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot: discord.ext.commands.Bot = bot
        self.channel_id = channel_id
        self.channel: typing.Optional[discord.TextChannel] = None
        self.posted_token_ids = None
        self.printer.start()

    color_mappings = {
        "Legendary": 0xB35A02,
        "Epic": 0x82008A,
        "Rare": 0x005F97,
        "Uncommon": 0x035F0A,
        "Common": 0xB7B7B7,
    }

    def cog_unload(self):
        self.printer.stop()

    @staticmethod
    def get_discord_message_id(token_id) -> bigquery.Row:
        client = bigquery.Client()
        query = f"""
        select discord_message_id from {TABLE_ID} where token_id = @token_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("token_id", "INTEGER", token_id)
            ]
        )
        query = client.query(query, job_config)
        return next(query.result())

    @staticmethod
    def get_token_ids_from_big_query() -> Set[int]:
        client = bigquery.Client()
        query = f"""
        select token_id from {TABLE_ID} 
        """
        query = client.query(query)
        return set(query.to_dataframe().token_id.values)

    @staticmethod
    def get_token_ids_from_storage() -> Set[int]:
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(BUCKET_NAME)
        return {
            int(blob.name.split("/")[-1][:-4])
            for blob in blobs
            if "v1/images" in blob.name
        }

    @staticmethod
    def get_token(token_id):
        storage_client = storage.Client.create_anonymous_client()
        bucket = storage_client.bucket("archive-mint")
        blob = bucket.blob(f"v1/metadata/{token_id}")
        metadata = blob.download_as_string().decode("utf8")
        return metadata

    @staticmethod
    def get_image(token_id):
        storage_client = storage.Client.create_anonymous_client()
        bucket = storage_client.bucket("archive-mint")
        blob = bucket.blob(f"v1/images/{token_id}.png")
        image_file_name = f"./image_{token_id}.png"
        blob.download_to_filename(image_file_name)
        return image_file_name

    @tasks.loop(seconds=LOOP_TIME_POOL_MINT_DATA)
    async def printer(self):
        token_ids_to_be_posted = self.get_token_ids_from_storage().difference(
            self.posted_token_ids
        )
        for token_id in token_ids_to_be_posted:
            token_meta_data = json.loads(self.get_token(token_id))
            color = None
            for x in token_meta_data["attributes"]:
                if x["trait_type"] == "Hash tier":
                    color = self.color_mappings[x["value"]]
                    break
            embed_mint = discord.Embed(
                title=f"Mint Event",
                description=f"{token_meta_data['name']}",
                color=color,
            )

            for attribute in token_meta_data["attributes"]:
                embed_mint.add_field(
                    name=f"{attribute['trait_type']}",
                    value=f"{attribute['value']}",
                    inline=False,
                )
            image_file_name = self.get_image(token_id=token_id)
            file = discord.File(image_file_name, filename=f"image_{token_id}.png")
            embed_mint.set_image(url=f"attachment://image_{token_id}.png")
            mint_post = await self.channel.send(embed=embed_mint, file=file)
            GcpUtils.insert_rows_bigquery(
                [{"discord_message_id": mint_post.id, "token_id": token_id}], TABLE_ID
            )
            self.posted_token_ids.add(token_id)

    @printer.before_loop
    async def before_printer(self):
        self.channel = await self.bot.fetch_channel(channel_id=self.channel_id)
        self.posted_token_ids = self.get_token_ids_from_big_query()

    @commands.check(only_owners)
    @commands.command()
    async def refresh_mint_post(self, ctx, token_id_str):
        """
        Currently not defined as it requires deleting a message
        :param ctx:
        :param token_id_str:
        :return:
        """
        pass

    @commands.check(only_owners)
    @commands.command()
    async def backfill_bq_from_history(self, ctx):
        historical_messages = await self.channel.history(limit=2047).flatten()
        tokens_data = pd.DataFrame(
            [
                {
                    "token_id": int(message.embeds[0].description.split("#")[1]),
                    "discord_message_id": message.id,
                }
                for message in historical_messages
            ]
        )
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )
        client = bigquery.Client()
        job = client.load_table_from_dataframe(
            tokens_data, TABLE_ID, job_config=job_config
        )
        job.result()


def setup(bot):
    bot.add_cog(MintPoster(bot=bot, channel_id=929017161618440264))
