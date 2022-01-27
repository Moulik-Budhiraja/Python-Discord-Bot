from .logging import Logging
import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from data import Data
data = Data()


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(guild_ids=data.enabled_slash, name='ppsize')
    async def ppsize(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=False, default=None)):
        """
        Returns the pp size of the user mentioned
        """
        import random

        discord_user = ctx.author if user is None else user

        # convert to custom user object
        try:
            user = data.get_user(
                ctx.author.id) if user is None else data.get_user(user.id)
        except:
            user = data.add_user(
                ctx.author.id, ctx.author.name, ctx.author.discriminator) if user is None else data.add_user(user.id, user.name, user.discriminator)

        # seed the random number generator with the user's id
        random.seed(user.id)

        if user.rigged:
            ppsize = random.randint(0, 2)
        elif user.goated:
            ppsize = random.randint(13, 15)
        else:
            ppsize = random.randint(0, 15)

        # generate response
        response = discord.Embed(
            title=f"{discord_user.name}'s PP Size",
            description=f"{discord_user.mention}'s PP Size: \n8{'=' * ppsize}D",
            color=0x00ffff
        )

        response = await ctx.respond(embed=response)

        Logging.log_command(ctx, action='Command',
                            extra=f"PPsize for user: {user.name}", response=response)

        return


def setup(client):
    client.add_cog(Games(client))
