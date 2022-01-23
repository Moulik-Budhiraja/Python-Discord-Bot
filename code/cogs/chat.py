import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from discord import Forbidden
from discord.commands import slash_command, Option

from exceptions import *
from data import Data

data = Data()  # Connect to database


class Chat(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        import re

        if message.author.bot:
            return

        # check if the channel is muted
        if data.get_guild(message.guild.id).get_channel(message.channel.id).muted_events:
            return

        # if the message contains 'hi', say 'hi'
        if re.search(r"hi", message.content):
            await message.channel.send('hi')

        # if message has I'm followed by a sentence, say "Hi <sentence>, I'm Jerald"
        if re.search(r"i'?m ([\s\w]+)\.?", message.content, re.IGNORECASE):
            sentence = re.search(
                r"i'?m ([\s\w]+)\.?", message.content, re.IGNORECASE).group(1)
            await message.channel.send(f"Hi {sentence}, I'm Jerald")

        # if the message is all caps
        if re.search(r"^[A-Z\s'!.?]+$", message.content):
            await message.channel.send(
                f"{message.author.mention} keep your voice down!")

    @slash_command(guild_ids=data.enabled_slash, name='mute_channel', description='Stop jerald from talking in this channel')
    async def mute_channel(
        self,
        ctx,
        channel: Option(discord.TextChannel, "Channel to mute",
                        required=False, default=None)
    ):
        """
        Mute the channel
        """
        # get the channel
        channel = ctx.channel if channel is None else channel

        # get the guild
        guild = data.get_guild(ctx.guild.id)

        # get the channel or add it if it doesn't exist
        try:
            channel = guild.get_channel(channel.id)
        except EntryNotFound:
            channel = guild.add_channel(channel.id, channel.name)

        # mute the channel
        channel.muted_events = True

        # send a response
        await ctx.respond(f"{channel.mention} is now muted")


def setup(client):
    client.add_cog(Chat(client))
