import discord
import asyncio
import httpx

with open('config/config.json') as f:
    config = json.load(f)
    token = config['token']

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58"
}

request = httpx.Client(headers=headers, timeout=None)

#intents = discord.Intents(guild_messages = True, guilds = True, messages = True, emojis = True, webhooks = True, message_content = True)
intents = discord.Intents.all()
client = discord.Client(intents=intents)

def url_has_image(url):
    # You can implement your own logic to check if the URL has an image
    # For example, you can use a library like BeautifulSoup to parse the HTML and look for image tags
    # Here, I'll simply assume that URLs ending with .jpg or .png have images
    return url.lower().endswith(('.jpg', '.png', '.gif'))


def parse(subreddit, after=''):
    url_template = "https://www.reddit.com/r/{}/hot.json?t=all{}"
    params = f'&after={after}' if after else ''

    url = url_template.format(subreddit, params)
    response = request.get(url)

    if response.status_code == httpx.codes.ok:
        data = response.json()['data']
        for post in data['children']:
            pdata = post['data']
            parse.title = pdata['title']
            parse.score = pdata['score']
            parse.author = pdata['author']
            parse.perma = pdata['permalink']
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
            title=f"{parse.title}", url=f"https://www.reddit.com{parse.perma}", description=f"u/{parse.author}", color=0x336EFF
        )
        embedVar.set_footer(icon_url="https://images-ext-2.discordapp.net/external/aujgdb0tjIpE_2cbuBl-xH0DhZ9mcOfeeJQ2ePze8HY/%3Fsize%3D96%26quality%3Dlossless/https/cdn.discordapp.com/emojis/906118310742077502.webp", text=f"{parse.score}")
        if url_has_image(parse.url):
          embedVar.set_image(url=f"{parse.url}")
        else:
          embedVar.add_field(name='', value=f"[click here to view]({parse.url})", inline=False)
        await msg.channel.send(embed=embedVar)

client.run(token)
