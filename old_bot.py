# TODO: 
#       Deal with if person spams command over and over
#       Test MAXSIZE limit
#       See how it works on 2 servers at once
#       Deal with *'s in message
#       Switch to buttons from reactions
#       Add help command
#       use embed rather than text

from discord.ext import commands
import urllib, json

bot = commands.Bot(command_prefix='!')

prior10Commands = {}
MAXSIZE = 10
# queryDict = {}
# queryDict["query"] = ""
# queryDict["author"] = 0
# queryDict["result"] = 0



@bot.command(name="printSequence", pass_context=True)
async def printing(ctx, *query: str):
    query = ''.join(query)
    query = query.replace(' ', '')

    search = "https://oeis.org/search?fmt=json&q=" + query + "&start=" + str(0)
    with urllib.request.urlopen(search) as url:
        data = json.loads(url.read().decode())
        if int(data["count"]) > 0 and data["results"] == None:
            await ctx.send("Too many results returned. Please make your request more specific")
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
        message = await ctx.send(firstResult["name"] + '\n' + sequence + '\n' + firstResult["formula"][0])
        prior10Commands[str(message.id)] = queryDict
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

@bot.event
async def on_reaction_add(reaction, user):
    if not user.bot:
        if reaction.emoji == '▶️':
            msg = reaction.message
            if str(msg.id) in prior10Commands and user.id == prior10Commands[str(msg.id)]["author"]:
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
                    await reaction.message.edit(content=(searchResult["name"] + '\n' + sequence + '\n' + searchResult["formula"][0]))
        elif reaction.emoji == '◀️':
            msg = reaction.message
            if str(msg.id) in prior10Commands and user.id == prior10Commands[str(msg.id)]["author"]:
                currentQueryDict = prior10Commands[str(msg.id)]
                currentResult = currentQueryDict["result"]
                newResult = 0
                if (currentResult == 0):
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
                    await reaction.message.edit(content=(searchResult["name"] + '\n' + sequence + '\n' + searchResult["formula"][0]))

with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)