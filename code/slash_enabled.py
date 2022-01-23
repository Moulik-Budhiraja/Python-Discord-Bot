from discord import Forbidden

from exceptions import EntryNotFound
from data import Data
data = Data()  # Connect to database


def fetch_slash_enabled(client):
    """
    Fetches which servers are able to use slash commands 
    """

    for guild in client.guilds:
        try:  # Make sure the guild is in the database
            data.get_guild(guild.id)
        except EntryNotFound:
            data.add_guild(guild.id, guild.name)

        try:
            # Try making initializing a slash command in the guild
            @client.slash_command(guild_ids=[guild.id], name='foo')
            async def foo(ctx): return

            # If successful, remove the slash command
            client.remove_application_command(foo)

            print(f'{guild.name} ({guild.id}) is enabled')

            # Mark the guild as having slash commands enabled
            data.get_guild(guild.id).slash_commands = True

        except Forbidden:
            # If an error is thrown, mark the guild as having slash commands disabled
            data.get_guild(guild.id).slash_commands = False

            print(f'{guild.name} ({guild.id}) is disabled')

    # Get a list of guilds that have slash commands enabled
    enabled_guilds = data.enabled_slash

    return enabled_guilds


if __name__ == '__main__':
    import discord
    from discord.ext import commands
    from dotenv import load_dotenv
    import os

    INTENTS = discord.Intents.all()  # Initialize Discord Bot
    client = commands.Bot(
        command_prefix='.',
        intents=INTENTS
    )

    load_dotenv()

    try:
        @client.slash_command(guild_ids=data.enabled_slash, name='foo')
        async def foo(ctx): return
    except Exception:
        print("Slash commands are disabled in this bot")

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
        fetch_slash_enabled(client)

    @client.on_connect.error
    async def on_connect_error(error, ctx):
        print(f'{ctx.command.name} failed to execute')
        print(error)

    client.run(os.getenv('TOKEN'))
