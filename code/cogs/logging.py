import discord
from discord.ext import commands
from discord.commands import Option

from data import Data
data = Data()


class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        data.add_log("Message", ctx=message)

    async def log_command(self, ctx, action=None, response=None, extra=None):
        # Log command
        data.add_log(
            "Command",
            action=action,
            extra=extra,
            user_id=ctx.author.id,
            guild_id=response.guild.id,
            channel_id=response.channel.id,
            message_text=response.content,
            message_id=response.id
        )


def setup(client):
    client.add_cog(Logging(client))
