# TODO:
#       Deal with if person spams command over and over
#       Test MAXSIZE limit
#       See how it works on 2 servers at once
#       Deal with *'s in message
#       use embed rather than text
#       test cases??????


from discord import activity
from discord.ext import commands
import urllib
import json
import discord

prior_10_commands: dict = {}
MAXSIZE = 3
# query_dict = {}
# query_dict["query"] = ""
# query_dict["author"] = 0
# query_dict["result"] = 0

class OEISbot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'))
        self.activity = discord.Game(name="!howTo")

bot = OEISbot()

class ScrollView(discord.ui.View):

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji(name='◀️'))
    async def scroll_backward(self, interaction: discord.Interaction):

        msg = interaction.message
        if str(msg.id) in prior_10_commands \
           and interaction.user.id == prior_10_commands[str(msg.id)]["author"]:

            current_query_dict = prior_10_commands[str(msg.id)]
            current_result = current_query_dict["result"]

            new_result: int = 0
            if current_result == 0:
                new_result = 0
            else:
                new_result = current_result - 1
            current_query_dict["result"] = new_result

            query = current_query_dict["query"]
            new_search = "https://oeis.org/search?fmt=json&q=" \
                        + query \
                        + "&start=" \
                        + str(new_result)

            prior_10_commands[str(msg.id)] = current_query_dict
            with urllib.request.urlopen(new_search) as url:
                data = json.loads(url.read().decode())
                search_result = data["results"][0]
                sequence: str = search_result["data"].replace(',', ", ")
                new_message:str = search_result["name"] + '\n' + sequence
                await interaction.response.edit_message(content=new_message, view=self)
    
    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji(name='▶️'))
    async def scroll_forward(self, interaction: discord.Interaction):
        msg = interaction.message
        if str(msg.id) in prior_10_commands \
           and interaction.user.id == prior_10_commands[str(msg.id)]["author"]:

            current_query_dict = prior_10_commands[str(msg.id)]
            current_result = current_query_dict["result"]

            max_count = current_query_dict["count"]
            new_result: int = 0
            if current_result == max_count - 1:
                new_result = current_result
            else:
                new_result = current_result + 1
            current_query_dict["result"] = new_result

            query = current_query_dict["query"]
            new_search = "https://oeis.org/search?fmt=json&q=" \
                        + query \
                        + "&start=" \
                        + str(new_result)

            prior_10_commands[str(msg.id)] = current_query_dict
            with urllib.request.urlopen(new_search) as url:
                data = json.loads(url.read().decode())
                search_result = data["results"][0]
                sequence: str = search_result["data"].replace(',', ", ")
                new_message:str = search_result["name"] + '\n' + sequence
                await interaction.response.edit_message(content=new_message, view=self)


@bot.command()
async def printSequence(ctx: commands.Context, *query: str):
    query = ''.join(query)
    query = query.replace(' ', '')

    search = "https://oeis.org/search?fmt=json&q=" + query + "&start=0"
    with urllib.request.urlopen(search) as url:
        data = json.loads(url.read().decode())
        if int(data["count"]) > 0 and data["results"] is None:
            await ctx.send(content="Too many results returned. Please make your request more specific")
            return
        
        query_dict = {}
        query_dict["query"] = query
        query_dict["result"] = 0
        query_dict["author"] = ctx.message.author.id
        

        # remove the oldest query
        if len(prior_10_commands) == MAXSIZE:
            del prior_10_commands[next(iter(prior_10_commands))]
        
        if int(data["count"]) == 0:
            message = await ctx.send("No results found.")
            return
        
        first_result = data["results"][0]
        query_dict["count"] = data["count"]
        sequence: str = first_result["data"].replace(',', ", ")
        search = first_result["name"] + '\n' + sequence
        message = await ctx.send(content=search, view=ScrollView())
        prior_10_commands[str(message.id)] = query_dict

@bot.command()
async def howTo(ctx: commands.Context):
    await ctx.send(
        content = "!printSequence: Find if a a string of number matches sequences from the OEIS.\n" \
                + "Example: !printSequence 1, 1, 2, 3, 5, 8\n" \
                + "You can add / omit spaces as desired."
    )
    return


with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)