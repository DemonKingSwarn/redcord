import discord
import asyncio
import httpx
import json
from discord import app_commands

headers = {
    "User-Agent": "RedCord/0.0.1"
}

request = httpx.Client(headers=headers, timeout=None)

with open('config/config.json') as f:
    config = json.load(f)
    token = config['token']

#intents = discord.Intents(guild_messages = True, guilds = True, messages = True, emojis = True, webhooks = True, message_content = True)
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def parse(subreddit, after=''):
    url_template = "https://www.reddit.com/r/{}/top.json?t=all{}"
    params = f'&after={after}' if after else ''

    url = url_template.format(subreddit, params)
    response = request.get(url)

    if response.status_code == httpx.codes.ok:
        data = response.json()['data']
        for post in data['children']:
            pdata = post['data']
            parse.title = pdata['title']
            parse.author = pdata['author']
            parse.url = pdata.get('url_overridden_by_dest')
            #print(f"\nTITLE: {parse.title}\nAUTHOR: {parse.author}\n{parse.url}\n\n\n")
        return data['after']
    else:
        print(f"Error {response.status_code}")
        return None

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1122485692044411020))
    print("logged in!")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    if msg.content.startswith("-reddit"):
        query = msg.content[8:]
        print(query)
        after = ''
        after = parse(query, after)
        embedVar = discord.Embed(
            title=f"{parse.title}", description=f"u/{parse.author}", color=0x336EFF
        )
        embedVar.set_image(url=f"{parse.url}")
        await msg.channel.send(embed=embedVar)

@tree.command(name = "reddit", description = "Search subreddit")
async def reddit(interaction):
    query = msg.content[8:]
    print(query)
    after = ''
    after = parse(query, after)
    embedVar = discord.Embed(
        title=f"{parse.title}", description=f"u/{parse.author}", color=0x336EFF
    )
    embedVar.set_image(url=f"{parse.url}")
    await interaction.response.send_message(embed=embedVar)



client.run(token)
