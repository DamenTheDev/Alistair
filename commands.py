import discord
import discordsql as dsql
import traceback


functions = []
function_calls = {}
bot = None


def cmd(description, parameters=None, required_parameters=None):
    def decorator(func):
        function_calls[func.__name__] = func
        functions.append({
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters if parameters is not None else {}
            },
            "required": required_parameters if required_parameters is not None else []
        })
        return func
    return decorator


@cmd("Send a message to a channel (supports markdown)", {"channel_id": {"type": "integer"}, "message": {"type": "string"}}, ["channel_id", "message"])
async def send_message(guild: discord.Guild, member, channel, channel_id: int, message: str):
    channel = guild.get_channel(channel_id)
    # See if the user is allowed to send messages to the channel
    if not channel.permissions_for(member).send_messages:
        print(f"[LEO] User {member.name}#{member.discriminator} ({member.id}) tried to send a message to {channel.name} ({channel.id}) but was denied")
        return "That user is not allowed to send messages to that channel"
    if channel is None:
        print(f"[LEO] Channel {channel_id} not found")
        return "Channel not found"
    try:
        await channel.send(message)
    except discord.Forbidden:
        print(f'[LEO] Forbidden to send message to {channel.name} ({channel.id})')
        return "Bot does not have permission to send messages to that channel"
    print(f"[LEO] Sent message to {channel.name}")
    return "Sent message"


@cmd("Runs SQL against the discord server (SELECT only) and save the selection to modify later.\n"
     "Tables: `members`, `channels`, `roles`, `bans`\nNote: In large servers, this may take a while to run.",
     {"sql": {"type": "string"}})
async def select_by_sql(guild, member, channel, sql):
    df = dsql.DiscordDataFrame(bot, guild)
    print('[LEO] Running SQL:', sql)
    try:
        results = await df.query(sql)
        results = results.values
    except Exception as e:
        print('[LEO] SQL returned error:', traceback.format_exc())
        return "SQL error: " + str(e)
    print('[LEO] SQL returned results:\n' + str(results))
    return str(results)





@cmd("Describes a table for use in SQL queries (uses the same tables as select_by_sql)", {"table": {"type": "string"}})
async def describe_table(guild, member, channel, table):
    df = dsql.DiscordDataFrame(bot, guild)
    print('[LEO] Describing table:', table)
    try:
        desc = await df.describe(table)
    except Exception as e:
        print('[LEO] Describing table failed with error:', str(e))
        return "Description error: " + str(e)
    print('[LEO] Describing table returned results:', desc)
    return desc
