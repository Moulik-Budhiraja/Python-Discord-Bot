import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, MissingPermissions
from discord import Forbidden
from discord.commands import slash_command, Option

from data import Data
data = Data()


class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash_command(guild_ids=data.enabled_slash, name='ping')
    async def ping(self, ctx):
        """
        Returns the bot's latency
        """
        return await ctx.respond(f'Pong! `{round(self.client.latency * 1000)}ms`')

    @slash_command(guild_ids=data.enabled_slash, name='mute')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=True, default=None),
            time: Option(int, "Minutes to mute the user for", required=False, default=10),
            reason: Option(str, "Reason for the mute", required=False, default="No reason provided.")):
        """
        Mutes a user for a specified amount of time
        """
        import datetime

        # Check if the bot has the permissions to mute the user
        if ctx.guild.me.top_role.position < user.top_role.position:
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{self.client.user.mention} does not have permission to mute {user.mention}\n'
                            f'raise {ctx.guild.me.top_role.mention} to be higher than {user.top_role.mention} to allow muting',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        # Timeout the user for the time specified
        await user.timeout_for(datetime.timedelta(minutes=time), reason=reason)

        response = discord.Embed(
            title='Muted User',
            description=f'{user.mention} has been muted for `{time}` minutes',
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @mute.error
    async def mute_error(self, ctx, error):
        """Handles errors for the mute command"""

        # Check if the user is missing a required argument
        if isinstance(error, MissingRequiredArgument):
            response = discord.Embed(
                title='Missing Argument',
                description=f'Please specify a user to mute',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        # Check if the user is missing permissions
        if isinstance(error, MissingPermissions):
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{ctx.author.mention} does not have the correct permissions to mute others\n'
                            f'Make sure you mave the `Moderate Members` permission',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, Forbidden):  # Check if the bot has missing permissions
            response = discord.Embed(
                title='Error',
                description=f'{ctx.guild.me.mention} does not have permission to unmute the target user',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        raise error

    @slash_command(guild_ids=data.enabled_slash, name='unmute')
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=True, default=None)):
        """
        Unmutes a user
        """
        # Check if the bot has the permissions to unmute the user
        if ctx.guild.me.top_role.position < user.top_role.position:
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{self.client.user.mention} does not have permission to unmute {user.mention}\n'
                            f'raise {ctx.guild.me.top_role.mention} to be higher than {user.top_role.mention} to allow unmuting',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        # Remove the timeout for the user
        await user.remove_timeout()

        # Generate response
        response = discord.Embed(
            title='Unmuted User',
            description=f'{user.mention} has been unmuted',
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @unmute.error
    async def unmute_error(self, ctx, error):
        """Handles errors for unmute"""

        # Check if the user is missing a required argument
        if isinstance(error, MissingRequiredArgument):
            response = discord.Embed(
                title='Missing Argument',
                description=f'Please specify a user to unmute',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        # Check if the user is missing permissions
        if isinstance(error, MissingPermissions):
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{ctx.author.mention} does not have the correct permissions to unmute others\n'
                            f'Make sure you mave the `Moderate Members` permission',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, Forbidden):  # Check if the bot has missing permissions
            response = discord.Embed(
                title='Error',
                description=f'{ctx.guild.me.mention} does not have permission to unmute the target user',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        raise error

    @slash_command(guild_ids=data.enabled_slash, name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=True, default=None),
            reason: Option(str, "Reason for the kick", required=False, default="No reason provided.")):
        """
        Kicks a user
        """
        # Kick the user
        await user.kick(reason=reason)

        # Generate response
        response = discord.Embed(
            title='Kicked User',
            description=f'{user.mention} has been kicked',
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @kick.error
    async def kick_error(self, ctx, error):
        """Handles errors for kick"""

        # Check if the user is missing a required argument
        if isinstance(error, MissingRequiredArgument):
            response = discord.Embed(
                title='Missing Argument',
                description=f'Please specify a user to kick',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        # Check if the user is missing permissions
        if isinstance(error, MissingPermissions):
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{ctx.author.mention} does not have the correct permissions to kick others\n'
                            f'Make sure you mave the `Kick Members` permission',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, Forbidden):  # Check if the bot has missing permissions
            response = discord.Embed(
                title='Error',
                description=f'{ctx.guild.me.mention} does not have permission to kick the target user',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        raise error

    @slash_command(guild_ids=data.enabled_slash, name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=True, default=None),
            reason: Option(str, "Reason for the ban", required=False, default="No reason provided.")):
        """
        Bans a user
        """
        # Ban the user
        await user.ban(reason=reason)

        # Generate response
        response = discord.Embed(
            title='Banned User',
            description=f'{user.mention} has been banned',
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @ban.error
    async def ban_error(self, ctx, error):
        """Handles errors for ban"""

        if isinstance(error, MissingRequiredArgument):
            response = discord.Embed(
                title='Missing Argument',
                description=f'Please specify a user to ban',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, MissingPermissions):
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{ctx.author.mention} does not have the correct permissions to ban others\n'
                            f'Make sure you mave the `Ban Members` permission',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, Forbidden):
            response = discord.Embed(
                title='Error',
                description=f'{ctx.guild.me.mention} does not have permission to ban the target user',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        raise error

    @slash_command(guild_ids=data.enabled_slash, name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
            self,
            ctx,
            user: Option(discord.Member, "Target user", required=True, default=None),
            reason: Option(str, "Reason for the unban", required=False, default="No reason provided.")):
        """
        Unbans a user
        """
        # Unban the user
        await ctx.guild.unban(user, reason=reason)

        # Generate response
        response = discord.Embed(
            title='Unbanned User',
            description=f'{user.mention} has been unbanned',
            color=0x00ff00
        )

        return await ctx.respond(embed=response)

    @unban.error
    async def unban_error(self, ctx, error):
        """Handles errors for unban"""

        if isinstance(error, MissingRequiredArgument):
            response = discord.Embed(
                title='Missing Argument',
                description=f'Please specify a user to unban',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, MissingPermissions):
            response = discord.Embed(
                title='Insufficient Permissions',
                description=f'{ctx.author.mention} does not have the correct permissions to unban others\n'
                            f'Make sure you mave the `Ban Members` permission',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        if isinstance(error, Forbidden):
            response = discord.Embed(
                title='Error',
                description=f'{ctx.guild.me.mention} does not have permission to unban the target user',
                color=0xff0000
            )

            return await ctx.respond(embed=response)

        raise error


def setup(client):
    client.add_cog(General(client))
