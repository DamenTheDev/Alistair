import discord
from discord.ext import commands
import pandas as pd
import pandasql as psql


class DiscordDataFrame:
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

    async def fetch_channels(self, _frame=False):
        if _frame:
            return 'id: int\nname: str'
        data = [{'id': channel.id, 'name': channel.name} for channel in self.guild.channels]
        if len(data) == 0:
            return False
        return pd.DataFrame(data)

    async def fetch_roles(self, _frame=False):
        if _frame:
            return 'id: int\nname: str'
        data = [{'id': role.id, 'name': role.name} for role in self.guild.roles]
        if len(data) == 0:
            return False
        return pd.DataFrame(data)

    async def fetch_members(self, _frame=False):
        if _frame:
            return 'id: int\nname: str'
        data = [{'id': member.id, 'name': member.name} for member in self.guild.members]
        if len(data) == 0:
            return False
        return pd.DataFrame(data)

    async def fetch_bans(self, _frame=False):
        if _frame:
            return 'id: int\nname: str\nreason: str'
        data = [{'id': ban.user.id, 'reason': ban.reason, 'name': ban.user.name} async for ban in self.guild.bans()]
        if len(data) == 0:
            return False
        return pd.DataFrame(data)

    async def describe(self, table):
        if table == 'channels':
            return await self.fetch_channels(True)
        if table == 'roles':
            return await self.fetch_roles(True)
        if table == 'members':
            return await self.fetch_members(True)
        if table == 'bans':
            return await self.fetch_bans(True)

        return "No such table: " + str(table)

    async def query(self, sql):
        channels = None
        roles = None
        members = None
        bans = None
        if 'channels' in sql.lower():
            channels = await self.fetch_channels()
        if 'roles' in sql.lower():
            roles = await self.fetch_roles()
        if 'members' in sql.lower():
            members = await self.fetch_members()
        if 'bans' in sql.lower():
            bans = await self.fetch_bans()

        empty = []

        if channels is False:
            empty.append('channels')
        if bans is False:
            empty.append('bans')
        if roles is False:
            empty.append('roles')
        if members is False:
            empty.append('members')

        suffix = ''
        if len(empty) > 0:
            suffix = '\nEmpty tables: ' + ', '.join(empty)

        try:
            return psql.sqldf(sql, locals()) + suffix
        except AttributeError:
            return "An error occured, this happens when the SQL is incorrect or the table you queried was empty." + suffix
