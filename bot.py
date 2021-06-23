from discord.ext import commands
import urllib, json

bot = commands.Bot(command_prefix='!')

@bot.command(name="printSequence")
async def printing(ctx, query: str):
    search = "https://oeis.org/search?fmt=json&q=" + query + "&start=0"
    with urllib.request.urlopen(search) as url:
        data = json.loads(url.read().decode())
        if int(data["count"]) > 0 and data["results"] == None:
            await ctx.send("Too many results returned. Please make your request more specific")
            return
        
        if int(data["count"]) == 0:
            await ctx.send("No results found.")
            return
        
        currentCount = int(data["count"])
        firstResult = data["results"][0]
        message = await ctx.send(firstResult["name"])
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')

with open("BOT_TOKEN.txt", "r") as token_file:
    TOKEN = token_file.read()
    print("Token file read")
    bot.run(TOKEN)