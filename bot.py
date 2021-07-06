# TODO: 
#       Pass query and result and stuff to reaction event
#       Make sure only person who sent command can edit message

from discord.ext import commands
import urllib, json, discord

bot = commands.Bot(command_prefix='!')

prior10Commands = {}
MAXSIZE = 10
# queryDict = {}
# queryDict["query"] = ""
# queryDict["author"] = 0
# queryDict["result"] = 0



@bot.command(name="printSequence", pass_context=True)
async def printing(ctx, query: str):

    search = "https://oeis.org/search?fmt=json&q=" + query + "&start=" + str(0)
    with urllib.request.urlopen(search) as url:
        data = json.loads(url.read().decode())
        if int(data["count"]) > 0 and data["results"] == None:
            await ctx.send("Too many results returned. Please make your request more specific")
            return
        
        queryDict = {}
        queryDict["query"] = query
        queryDict["result"] = 0
        prior10Commands[str(ctx.message.author.id)] = queryDict
        
        if int(data["count"]) == 0:
            await ctx.send("No results found.")
            return
        
        firstResult = data["results"][0]
        message = await ctx.send(firstResult["name"] + '\n' + 'Result: 0' + '\n' + 'Query: ' + query)
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        print("bot self reacted")
    else:
        msg = reaction.message
        if str(user.id) in prior10Commands:
            currentQueryDict = prior10Commands[str(user.id)]
            currentResult = currentQueryDict["result"]
            newResult = currentResult + 1
            currentQueryDict["result"] = newResult
            query = currentQueryDict["query"]
            newSearch = "https://oeis.org/search?fmt=json&q=" + query + "&start=" + str(newResult)
            prior10Commands[str(msg.id)] = currentQueryDict
            with urllib.request.urlopen(newSearch) as url:
                data = json.loads(url.read().decode())
                searchResult = data["results"][0]
                await reaction.message.edit(content=searchResult["name"])

with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)