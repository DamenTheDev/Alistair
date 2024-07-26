import openai
import json
import datetime
import traceback


openai.api_key = 'apikey'
ENGINE = "gpt-4-0613"
with open('prompt.txt') as f:
    prompt = f.read()


functions = []
function_calls = {}
conversations = {}
conversation_timeout = datetime.timedelta(minutes=5)
DONT_CONTINUE = 13


def delete_conv(user_id, channel_id):
    if str(user_id) + "-" + str(channel_id) in conversations:
        conversations[str(user_id) + "-" + str(channel_id)].running = False
        del conversations[str(user_id) + "-" + str(channel_id)]
        return DONT_CONTINUE
    return DONT_CONTINUE


class Conversation(object):
    def __init__(self):
        self.last_message = datetime.datetime.now()
        self.user = None
        self.guild = None
        self.channel = None
        self.running = True
        self.messages = None

    @staticmethod
    def generate(user_id, channel_id, author=None, guild=None, channel=None):
        if str(user_id) + "-" + str(channel_id) in conversations:
            conv = conversations[str(user_id) + "-" + str(channel_id)]
            if datetime.datetime.now() - conv.last_message > conversation_timeout:
                del conversations[str(user_id) + "-" + str(channel_id)]
                return Conversation.generate(user_id, channel_id, author, guild, channel)
            return conv
        conv = Conversation()
        conv.user = author
        conv.guild = guild
        conv.channel = channel
        conv.messages = [{"role": "system", "content": prompt+'\n(Channel: '+str(conv.channel.id)+' ' +str(conv.channel.name)+ ')'}]
        conversations[str(user_id) + "-" + str(channel_id)] = conv
        return conv

    def add_message(self, message: str, role="user", name=None):
        to_add: dict[str, str] = {"role": role, "content": message}
        if name is not None:
            to_add["name"] = name
        self.messages.append(to_add)

    def pretty_print(self):
        for message in self.messages:
            print(f"{message['role']}: {message['content']}")

    async def ask(self):
        if not self.running:
            return
        if len(functions) == 0:
            response = openai.ChatCompletion.create(
                model=ENGINE,
                messages=self.messages,
            )
        else:
            response = openai.ChatCompletion.create(
                model=ENGINE,
                messages=self.messages,
                functions=functions,
                function_call="auto"
            )
        msg = response.choices[0].message
        self.messages.append(msg)

        # Process message
        if msg.get("function_call"):
            function_name = str(msg["function_call"]["name"])
            function_args = json.loads(msg["function_call"]["arguments"])
            try:
                if function_name in function_calls:
                    function_result = str(await function_calls[function_name](self.guild, self.user, self.channel,
                                                                              **function_args))
                else:
                    function_result = "Command does not exist"

            except Exception as e:
                print('[FUNC] Error:', traceback.format_exc())
                function_result = "Error: " + str(e)
            build: dict[str, str] = {
                "role": "function",
                "name": function_name,
                "content": function_result
            }
            self.messages.append(build)
            if function_result != DONT_CONTINUE:
                return await self.ask()
            self.running = False
            return

        elif msg.get("content") is not None:
            #self.pretty_print()
            self.last_message = datetime.datetime.now()
            if not self.running:
                return
            return msg["content"]

        else:
            print("Error: No content in message")
            print(msg)
