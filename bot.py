from discord.ext import commands
import urllib, json
import discord

prior10Commands = {}
MAXSIZE = 10
# queryDict = {}
# queryDict["query"] = ""
# queryDict["author"] = 0
# queryDict["result"] = 0

class oeis_bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'))
    
    async def on_ready(self):
        print("ready")

bot = oeis_bot()

class scroll_view(discord.ui.View):

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji(name='◀️'))
    async def scrollBackward(self, button: discord.ui.Button, interaction: discord.Interaction):
        msg = interaction.message
        if str(msg.id) in prior10Commands and interaction.user.id == prior10Commands[str(msg.id)]["author"]:
            currentQueryDict = prior10Commands[str(msg.id)]
            currentResult = currentQueryDict["result"]
            newResult: int = 0
            if currentResult == 0:
                newResult = 0
            else:
                newResult = currentResult - 1
            currentQueryDict["result"] = newResult
            query = currentQueryDict["query"]
            newSearch = "https://oeis.org/search?fmt=json&q=" + query + "&start=" + str(newResult)
            prior10Commands[str(msg.id)] = currentQueryDict
            with urllib.request.urlopen(newSearch) as url:
                data = json.loads(url.read().decode())
                searchResult = data["results"][0]
                sequence: str = searchResult["data"].replace(',', ", ")
                new_message:str = searchResult["name"] + '\n' + sequence
                await interaction.response.edit_message(content=new_message, view=self)
    
    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji(name='▶️'))
    async def scrollForward(self, button: discord.ui.Button, interaction: discord.Interaction):
        msg = interaction.message
        if str(msg.id) in prior10Commands and interaction.user.id == prior10Commands[str(msg.id)]["author"]:
            currentQueryDict = prior10Commands[str(msg.id)]
            currentResult = currentQueryDict["result"]
            maxCount = currentQueryDict["count"]
            newResult: int = 0
            if currentResult == maxCount - 1:
                newResult = currentResult
            else:
                newResult = currentResult + 1
            currentQueryDict["result"] = newResult
            query = currentQueryDict["query"]
            newSearch = "https://oeis.org/search?fmt=json&q=" + query + "&start=" + str(newResult)
            prior10Commands[str(msg.id)] = currentQueryDict
            with urllib.request.urlopen(newSearch) as url:
                data = json.loads(url.read().decode())
                searchResult = data["results"][0]
                sequence: str = searchResult["data"].replace(',', ", ")
                new_message:str = searchResult["name"] + '\n' + sequence
                await interaction.response.edit_message(content=new_message, view=self)


@bot.command()
async def printSequence(ctx: commands.Context, *query: str):
    query = ''.join(query)
    query = query.replace(' ', '')

    search = "https://oeis.org/search?fmt=json&q=" + query + "&start=0"
    with urllib.request.urlopen(search) as url:
        data = json.loads(url.read().decode())
        if int(data["count"]) > 0 and data["results"] == None:
            await ctx.send(content="Too many results returned. Please make your request more specific")
            return
        
        queryDict = {}
        queryDict["query"] = query
        queryDict["result"] = 0
        queryDict["author"] = ctx.message.author.id
        

        # remove the oldest query
        if len(prior10Commands) == MAXSIZE:
            del prior10Commands[next(iter(prior10Commands))]
        
        if int(data["count"]) == 0:
            message = await ctx.send("No results found.")
            return
        
        firstResult = data["results"][0]
        queryDict["count"] = data["count"]
        sequence: str = firstResult["data"].replace(',', ", ")
        search = firstResult["name"] + '\n' + sequence
        message = await ctx.send(content=search, view=scroll_view())
        prior10Commands[str(message.id)] = queryDict


with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)