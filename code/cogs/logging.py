from exceptions import *
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.commands import Option

from data import Data
data = Data()


class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        """On message event log message data"""
        # Fetches the required classes from database
        try:
            user = data.get_user(message.author.id)
        except EntryNotFound:
            user = data.add_user(
                message.author.id, message.author.name, message.author.discriminator)

        try:
            guild = data.get_guild(message.guild.id)
        except EntryNotFound:
            guild = data.add_guild(message.guild.id, message.guild.name)

        try:
            channel = guild.get_channel(message.channel.id)
        except EntryNotFound:
            channel = guild.add_channel(
                message.channel.id, message.channel.name)

        # Add the log
        data.add_log(
            action="Message",
            user_id=user.id,
            guild_id=guild.id,
            channel_id=channel.id,
            message_id=message.id,
            message_text=message.content
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """On message edit event log new message data"""
        # Fetches the required classes from database
        try:
            user = data.get_user(after.author.id)
        except EntryNotFound:
            user = data.add_user(
                after.author.id, after.author.name, after.author.discriminator)

        try:
            guild = data.get_guild(after.guild.id)
        except EntryNotFound:
            guild = data.add_guild(after.guild.id, after.guild.name)

        try:
            channel = guild.get_channel(after.channel.id)
        except EntryNotFound:
            channel = guild.add_channel(after.channel.id, after.channel.name)

        # Add the log
        data.add_log(
            action="Message Edit",
            extra=f"Before: {before.content}",
            user_id=user.id,
            guild_id=guild.id,
            channel_id=channel.id,
            message_id=after.id,
            message_text=after.content
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """On message delete event log original message data"""
        # Fetches the required classes from database
        try:
            user = data.get_user(message.author.id)
        except EntryNotFound:
            user = data.add_user(
                message.author.id, message.author.name, message.author.discriminator)

        try:
            guild = data.get_guild(message.guild.id)
        except EntryNotFound:
            guild = data.add_guild(message.guild.id, message.guild.name)

        try:
            channel = guild.get_channel(message.channel.id)
        except EntryNotFound:
            channel = guild.add_channel(
                message.channel.id, message.channel.name)

        # Add the log
        data.add_log(
            action="Message Delete",
            user_id=user.id,
            guild_id=guild.id,
            channel_id=channel.id,
            message_id=message.id,
            message_text=message.content
        )

    @staticmethod
    async def log_command(ctx, action=None, extra=None):
        # Fetches the required classes from database
        try:
            user = data.get_user(ctx.author.id)
        except EntryNotFound:
            user = data.add_user(
                ctx.author.id, ctx.author.name, ctx.author.discriminator)

        try:
            guild = data.get_guild(ctx.guild.id)
        except EntryNotFound:
            guild = data.add_guild(ctx.guild.id, ctx.guild.name)

        try:
            channel = guild.get_channel(ctx.channel.id)
        except EntryNotFound:
            channel = guild.add_channel(
                ctx.channel.id, ctx.channel.name)

        try:
            message_id = ctx.message.id
        except AttributeError:
            message_id = None

        try:
            message_content = ctx.message.content
        except AttributeError:
            message_content = None

        # Add the log
        data.add_log(
            action=action,
            extra=extra,
            user_id=user.id,
            guild_id=guild.id,
            channel_id=channel.id,
            message_id=message_id,
            message_text=message_content
        )


def setup(client):
    client.add_cog(Logging(client))
