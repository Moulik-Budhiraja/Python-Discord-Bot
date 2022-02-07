import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from discord import Forbidden
from discord.commands import slash_command, Option, SlashCommandGroup

import asyncio

from exceptions import *
from data import Data

from .logging import Logging
data = Data()  # Connect to database


class AutoMod(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitors messages and checks if moderation is needed"""
        import re
        import datetime

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

        # Check if message violates any rules
        if not guild.auto_mod.enabled:
            return

        consequnce = None
        timeout_time = None

        for rule in guild.auto_mod.custom_config:
            if rule.type == "word":
                if rule.value in message.content.lower().split():
                    # Set to the highest consequence
                    if consequnce is None:
                        consequnce = rule.consequence
                    elif rule.consequence == "ban":
                        consequnce = rule.consequence
                    elif consequnce != "ban" and rule.consequence == "kick":
                        consequnce = rule.consequence
                    elif consequnce != "kick" and rule.consequence == "timeout":
                        consequnce = rule.consequence
                        timeout_time = rule.timeout_time
                    elif consequnce != "timeout" and rule.consequence == "delete":
                        consequnce = rule.consequence

            elif rule.type == "regex":
                if re.search(rule.value, message.content):
                    # Set to the highest consequence
                    if consequnce is None:
                        consequnce = rule.consequence
                    elif rule.consequence == "ban":
                        consequnce = rule.consequence
                    elif consequnce != "ban" and rule.consequence == "kick":
                        consequnce = rule.consequence
                    elif consequnce != "kick" and rule.consequence == "timeout":
                        consequnce = rule.consequence
                        timeout_time = rule.timeout_time
                    elif consequnce != "timeout" and rule.consequence == "delete":
                        consequnce = rule.consequence

        # If there is a consequnce, do the action
        if consequnce is not None:
            if consequnce == "ban":
                await message.author.ban()
            elif consequnce == "kick":
                await message.author.kick()
            elif consequnce == "timeout":
                await message.author.timeout_for(datetime.timedelta(minutes=timeout_time))

            message.delete()

            # Add the log

            data.add_log(
                action="AutoMod Action",
                user_id=user.id,
                guild_id=guild.id,
                extra=f"Action: {consequnce}",
            )

        if guild.auto_mod.anti_spam:

            # Refresh the database
            guild.auto_mod.anti_spam = guild.auto_mod.anti_spam

            # Get logs
            logs = user.get_logs(
                limit=guild.auto_mod.anti_spam,
                time=datetime.datetime.now() - datetime.timedelta(seconds=15),
                guild=guild.id,
                action="Message"
            )

            # Check if the user has sent the same message over and over
            if len(logs) == guild.auto_mod.anti_spam and len({log.message_text for log in logs}) == 1:
                # Delete all spam messages sent by the user
                for log in logs:
                    try:
                        message = await message.channel.fetch_message(log.message_id)
                        await message.delete()
                    except discord.NotFound:
                        pass

                # Timeout the user
                try:
                    await message.author.timeout_for(datetime.timedelta(minutes=10), reason="Spamming")
                except Forbidden:
                    pass

    automod = SlashCommandGroup(
        "automod", "AutoMod commands", guild_ids=data.enabled_slash)

    @ automod.command()
    async def enable(self, ctx):
        """
        Enable AutoMod in this server
        """
        guild_data = data.get_guild(ctx.guild.id)

        if guild_data.auto_mod.enabled:
            response = discord.Embed(
                title="AutoMod is already enabled",
                description="AutoMod is already enabled in this server",
                color=0xffff00
            )

            response = await ctx.respond(embed=response)

            return await Logging.log_command(ctx, action='Command',
                                             extra=f"{ctx.author.name} tried to enable AutoMod")

        guild_data.auto_mod.enabled = True

        response = discord.Embed(
            title='AutoMod Enabled',
            description='AutoMod has been enabled in this server.',
            color=0x00ff00)

        response = await ctx.respond(embed=response)

        await Logging.log_command(ctx, action='Command', extra=f"{ctx.author.name} enabled AutoMod")

    @ automod.command()
    async def disable(self, ctx):
        """
        Disable AutoMod in this server
        """
        guild_data = data.get_guild(ctx.guild.id)

        if not guild_data.auto_mod.enabled:
            response = discord.Embed(
                title="AutoMod is already disabled",
                description="AutoMod is already disabled in this server",
                color=0xffff00
            )

            response = await ctx.respond(embed=response)

            return await Logging.log_command(ctx, action='Command',
                                             extra=f"{ctx.author.name} tried to disable AutoMod")

        guild_data.auto_mod.enabled = False

        response = discord.Embed(
            title='AutoMod Disabled',
            description='AutoMod has been disabled in this server.',
            color=0x00ff00)

        response = ctx.respond(embed=response)

        await Logging.log_command(ctx, action='Command', extra=f"{ctx.author.name} disabled AutoMod")

    @ automod.command()
    async def anti_spam(self, ctx, threshold: Option(int, "Threshold for spam (0 to disable)", required=True, default=3)):
        """Sets the threshold for spam"""
        guild_data = data.get_guild(ctx.guild.id)

        if threshold < 0:
            response = discord.Embed(
                title="Invalid threshold",
                description="Threshold must be greater than or equal to 0",
                color=0xffff00
            )

            response = await ctx.respond(embed=response)

            return await Logging.log_command(ctx, action='Command',
                                             extra=f"{ctx.author.name} tried to set an invalid threshold")

        elif threshold == 0:
            guild_data.auto_mod.anti_spam = threshold

            response = discord.Embed(
                title="Anti-Spam Disabled",
                description="Anti-Spam has been disabled in this server.",
                color=0x00ff00)

            response = await ctx.respond(embed=response)

            return await Logging.log_command(ctx, action='Command', extra=f"{ctx.author.name} disabled anti-spam")

        guild_data.auto_mod.anti_spam = threshold

        response = discord.Embed(
            title='Threshold Set',
            description=f'Threshold has been set to {threshold}',
            color=0x00ff00)

        response = await ctx.respond(embed=response)

        await Logging.log_command(ctx, action='Command', extra=f"{ctx.author.name} set threshold to {threshold}")


def setup(client):
    client.add_cog(auto_mod := AutoMod(client))
