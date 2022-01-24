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
        if re.search(r"\bi'?m ([\s\w]+)\.?", message.content, re.IGNORECASE):
            sentence = re.search(
                r"\bi'?m ([\s\w]+)\.?", message.content, re.IGNORECASE).group(1)
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
                        required=False, default=None),
        all: Option(bool, "Mute all channels", required=False, default=False)
    ):
        """
        Mute the channel
        """
        # get the channel
        channel = ctx.channel if channel is None else channel

        # get the guild
        guild_data = data.get_guild(ctx.guild.id)

        if all:
            channels_muted = []
            for channel in ctx.guild.channels:
                try:
                    channel_data = guild_data.get_channel(channel.id)
                except EntryNotFound:
                    channel_data = guild_data.add_channel(
                        channel.id, channel.name)  # add the channel to the database

                if channel_data.muted_events == False:
                    channel_data.muted_events = True
                    # add channel to list of muted channels
                    channels_muted.append(channel)

            # Mention each channel
            channels_muted = [c.mention for c in channels_muted]

            # Joined string
            channels_muted = '\n'.join(channels_muted)

            # Send response
            response = discord.Embed(
                title="Channels Unmuted",
                description=f"The following channels have been muted:\n{channels_muted}",
                color=0x00ff00
            )

            return await ctx.respond(embed=response)

        # get the channel or add it if it doesn't exist
        try:
            channel_data = guild_data.get_channel(channel.id)
        except EntryNotFound:
            channel_data = guild_data.add_channel(channel.id, channel.name)

        # Check if the channel is already muted
        if channel_data.muted_events:
            response = discord.Embed(
                title="Channel already muted",
                description=f"{channel.mention} is already muted",
                color=0xFFff00
            )

            return await ctx.respond(embed=response)

        # mute the channel
        channel_data.muted_events = True

        # send a response
        response = discord.Embed(
            title="Channel Muted",
            description=f"{channel.mention} has been muted",
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @slash_command(guild_ids=data.enabled_slash, name='unmute_channel', description='Allow jerald to talk in this channel')
    async def unmute_channel(
        self,
        ctx,
        channel: Option(discord.TextChannel, "Channel to unmute",
                        required=False, default=None),
        all: Option(bool, "Unmute all channels", required=False, default=False)
    ):
        """
        Unmute the channel
        """
        # get the channel
        channel = ctx.channel if channel is None else channel

        # get the guild
        guild_data = data.get_guild(ctx.guild.id)

        if all:
            # unmute all channels
            channels_muted = []
            for channel in ctx.guild.channels:
                try:
                    channel_data = guild_data.get_channel(channel.id)
                except EntryNotFound:
                    # add the channel if it doesn't exist
                    channel_data = guild_data.add_channel(
                        channel.id, channel.name)

                if channel_data.muted_events:  # if the channel is muted
                    channel_data.muted_events = False
                    # add each channel unmuted to the list
                    channels_muted.append(channel)

            # Mention each channel
            channels_muted = [c.mention for c in channels_muted]

            # Joined string
            channels_muted = '\n'.join(channels_muted)

            # Send a response
            response = discord.Embed(
                title="Channels Unmuted",
                description=f"The following channels have been unmuted:\n{channels_muted}",
                color=0x00ff00
            )

            return await ctx.respond(embed=response)

        # get the channel or add it if it doesn't exist
        try:
            channel_data = guild_data.get_channel(channel.id)
        except EntryNotFound:
            channel_data = guild_data.add_channel(channel.id, channel.name)

        # Check if the channel is already unmuted
        if channel_data.muted_events == False:
            response = discord.Embed(
                title="Channel Unmuted",
                description=f"{channel.mention} is already unmuted",
                color=0xffff00
            )

            return await ctx.respond(embed=response)

        # unmute the channel
        channel_data.muted_events = False

        # send a response
        response = discord.Embed(
            title="Channel Unmuted",
            description=f"{channel.mention} has been unmuted",
            color=0x00ff00
        )

        return await ctx.respond(embed=response)


def setup(client):
    client.add_cog(Chat(client))
