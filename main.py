import discord
from discord.ext import commands
import oai
import commands as cmds
import datetime
import discordsql as dsql


class Alistair(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, help_command=None, intents=discord.Intents.all())

    async def on_message(self, message: discord.Message, /) -> None:
        if message.author.bot or not self.user.mentioned_in(message):
            if str(message.author.id) + "-" + str(message.channel.id) in oai.conversations:
                conv = oai.conversations[str(message.author.id) + "-" + str(message.channel.id)]
                if datetime.datetime.now() - conv.last_message > oai.conversation_timeout or not conv.running:
                    del oai.conversations[str(message.author.id) + "-" + str(message.channel.id)]
                    return
            else:
                return

        content = message.content
        attachments = message.attachments
        print(attachments)
        conv = oai.Conversation.generate(message.author.id, message.channel.id, message.author, message.guild,
                                         message.channel)
        if len(conv.messages) == 1:
            await message.channel.send(f'**Conversation start ({message.channel.mention}, {message.author.mention})**')
        conv.add_message(str(content), name=str(message.author.id))

        async with message.channel.typing():
            m = await conv.ask()
            if m is not None and conv.running:
                await message.reply(m, mention_author=False, allowed_mentions=discord.AllowedMentions.none())
                return
        await message.reply("**Conversation closed**", mention_author=False)


@cmds.cmd("Ends the conversation, only do this if the user doesn't seem to be talking to you anymore or if specifically asked to")
async def end_conversation(guild: discord.Guild, member: discord.Member, channel: discord.TextChannel):
    print(f"[LEO] Ending conversation with {member.name} in {channel.name}")
    return oai.delete_conv(member.id, channel.id)


bot = Alistair()
oai.functions = cmds.functions
oai.function_calls = cmds.function_calls
oai.bot = bot


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


if __name__ == "__main__":
    bot.run("token")
