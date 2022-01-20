from urllib import response
import discord
from discord.ext import commands
from discord.ext.commands import ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded

import os
from dotenv import load_dotenv


INTENTS = discord.Intents.all()
client = commands.Bot(
    command_prefix='.',
    intents=INTENTS
)


@client.command()  # LOADS COG
async def load(ctx, name: str, *args):
    """
    Loads an extension

    `.load <name>`
    """

    try:
        client.load_extension(f'cogs.{name}')

        response = discord.Embed(
            title='Loaded Extension',
            description=f'`{name}` has been loaded',
            color=0x00ff00
        )

        await ctx.send(embed=response)

    except ExtensionNotFound:
        response = discord.Embed(
            title='Extension Not Found',
            description=f'`{name}` does not exist',
            color=0xff0000
        )

        await ctx.send(embed=response)

    except ExtensionAlreadyLoaded:
        response = discord.Embed(
            title='Extension Already Loaded',
            description=f'`{name}` is already loaded',
            color=0xff0000
        )

        await ctx.send(embed=response)


@client.command()  # UNLOADS COG
async def unload(ctx, name: str, *args):
    """
    Unloads an extension

    `.unload <name>`
    """

    try:
        client.unload_extension(f'cogs.{name}')

        response = discord.Embed(
            title='Unloaded Extension',
            description=f'`{name}` has been unloaded',
            color=0x00ff00
        )

        await ctx.send(embed=response)

    except ExtensionNotLoaded:
        response = discord.Embed(
            title='Extension Not Loaded',
            description=f'`{name}` is not loaded',
            color=0xff0000
        )

        await ctx.send(embed=response)


@client.command()  # RELOADS COG
async def reload(ctx, name: str, *args):
    """
    Reloads an extension

    `.reload <name>`
    """

    try:
        client.unload_extension(f'cogs.{name}')
        client.load_extension(f'cogs.{name}')

        response = discord.Embed(
            title='Reloaded Extension',
            description=f'`{name}` has been reloaded',
            color=0x00ff00
        )

        await ctx.send(embed=response)

    except ExtensionNotLoaded:
        response = discord.Embed(
            title='Extension Not Loaded',
            description=f'`{name}` is not loaded',
            color=0xff0000
        )

        await ctx.send(embed=response)

client.run(os.getenv('TOKEN'))
