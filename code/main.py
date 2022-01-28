from urllib import response
import discord
from discord.ext import commands
from discord import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded
from discord.commands import Option, permissions

import os
from dotenv import load_dotenv

from exceptions import *
from data import Data


data = Data()  # Connect to database


INTENTS = discord.Intents.all()  # Initialize Discord Bot
client = commands.Bot(
    command_prefix='.',
    intents=INTENTS
)

# LOADS COG


@client.slash_command(guild_ids=data.enabled_slash, name='load')
@permissions.is_user(int(os.getenv("BOT_OWNER_ID")))
async def load(
    ctx,
    name: Option(str, "The name of the extension", required=True, default=None)
):
    """
    Loads an extension
    """

    try:
        client.load_extension(f'cogs.{name}')

        response = discord.Embed(
            title='Loaded Extension',
            description=f'`{name}` has been loaded',
            color=0x00ff00
        )

        await ctx.respond(embed=response)

    except ExtensionNotFound:
        response = discord.Embed(
            title='Extension Not Found',
            description=f'`{name}` does not exist',
            color=0xff0000
        )

        await ctx.respond(embed=response)

    except ExtensionAlreadyLoaded:
        response = discord.Embed(
            title='Extension Already Loaded',
            description=f'`{name}` is already loaded',
            color=0xff0000
        )

        await ctx.respond(embed=response)

''' # Unload and Reload Commands
    # # UNLOADS COG
    # @client.slash_command(guild_ids=data.enabled_slash, name='unload')
    # async def unload(
    #     ctx,
    #     name: Option(str, "The name of the extension", required=True, default=None)
    # ):
    #     """
    #     Unloads an extension
    #     """

    #     try:
    #         client.remove_cog(f'cogs.{name}')
    #         client.unload_extension(f'cogs.{name}')

    #         response = discord.Embed(
    #             title='Unloaded Extension',
    #             description=f'`{name}` has been unloaded',
    #             color=0x00ff00
    #         )

    #         await ctx.respond(embed=response)

    #     except ExtensionNotLoaded:
    #         response = discord.Embed(
    #             title='Extension Not Loaded',
    #             description=f'`{name}` is not loaded',
    #             color=0xff0000
    #         )

    #         await ctx.respond(embed=response)


    # # RELOADS COG
    # @client.slash_command(guild_ids=data.enabled_slash, name='reload')
    # async def reload(
    #     ctx,
    #     name: Option(str, "The name of the extension", required=True, default=None)
    # ):
    #     """
    #     Reloads an extension
    #     """

    #     try:
    #         client.remove_cog(f'cogs.{name}')
    #         client.unload_extension(f'cogs.{name}')
    #         client.load_extension(f'cogs.{name}')

    #         response = discord.Embed(
    #             title='Reloaded Extension',
    #             description=f'`{name}` has been reloaded',
    #             color=0x00ff00
    #         )

    #         await ctx.respond(embed=response)

    #     except ExtensionNotLoaded:
    #         response = discord.Embed(
    #             title='Extension Not Loaded',
    #             description=f'`{name}` is not loaded',
    #             color=0xff0000
    #         )

    #         await ctx.respond(embed=response)
'''


@client.slash_command(guild_ids=data.enabled_slash, name='auto-load')
@permissions.is_user(int(os.getenv("BOT_OWNER_ID")))
async def auto_load(
    ctx,
    name: Option(str, "The name of the extension", required=True, default=None),
    enabled: Option(bool, "Whether or not to enable auto-load",
                    required=False, default=True)
):
    """
    Set an extension to automaticly load
    """

    try:
        data.get_cog(name).enabled = enabled
    except EntryNotFound:  # If the cog doesn't exist send an error message
        response = discord.Embed(
            title='Extension Not Found',
            description=f'`{name}` does not exist',
            color=0xff0000
        )

        return await ctx.respond(embed=response)

    # Send a response based on the action
    if enabled:
        response = discord.Embed(
            title='Auto-Load',
            description=f'`{name}` will now automatically load',
            color=0x00ff00
        )
    else:
        response = discord.Embed(
            title='Auto-Load',
            description=f'`{name}` will no longer automatically load',
            color=0x00ff00
        )

    await ctx.respond(embed=response)


@client.slash_command(guild_ids=data.enabled_slash, name='shutdown', default_permission=False)
@permissions.is_user(int(os.getenv("BOT_OWNER_ID")))
async def shutdown(ctx):
    """
    Shuts down the bot
    """
    await ctx.respond('Shutting down...')
    await client.close()


@client.event
async def on_ready():
    print(f'{client.user} is ready!')


# Load enabled cogs
for cog in data.cogs:
    if cog.enabled:
        client.load_extension(f'cogs.{cog.name}')

client.run(os.getenv('TOKEN'))
