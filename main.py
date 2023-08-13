import discord, json, sellapp, requests, os, asyncio, threading, flask, quart, random, signal
from discord.ext import tasks
from discord import option
from quart import request



config = {
        "token": os.environ.get('token'),
        "keys": {
            "clicker": {
                "1week": {
                    "URL": os.environ.get('clicker1week')
                }
            },
            "client": {
                "1week": {
                    "URL": os.environ.get('client1week')
                }
            }
        }
    }

bot = discord.Bot(intents=discord.Intents.all())

@bot.slash_command()
@option("forwhat", description="Clicker or Client?", required=True, choices=["Client", "Clicker"])
async def join(ctx: discord.ApplicationContext, forwhat = str):
    with open('settings.json', 'r') as f:
        r = json.load(f)
    
    if forwhat == "Clicker":
        inTimeoutClicker = r['clicker']['timeouts'].keys()
        for xy in inTimeoutClicker:
            if str(xy) == str(ctx.author.id):
                return await ctx.respond(f"**You are in Timeout.\nYou need to wait {r['clicker']['timeouts'][str(ctx.author.id)]['time']}d till you can reedem another key.\nBug? Open a ticket.**")
    
    if forwhat == "Client":
        inTimeoutClient = r['client']['timeouts'].keys()   
        for xy in inTimeoutClient:
            if str(xy) == str(ctx.author.id):
                return await ctx.respond(f"**You are in Timeout.\nYou need to wait {r['client']['timeouts'][str(ctx.author.id)]['time']}d till you can reedem another key.\nBug? Open a ticket.**")
    
    await ctx.respond(':eyes: **Look at your DMs for more informations.**')
    
    if forwhat == "Clicker":
        embed = discord.Embed()
        embed.title = "Physiological Clicker Queue"
        embed.description = f"You are now in the queue. I will ping you again when your key is ready.\nRemaining hours: **12h**"
        embed.color = discord.Color.blurple()
        embed.set_footer(text="You can buy to get a key instantly!")
    
        msg = await ctx.author.send(embed=embed)
    
        r['clicker']['users'][str(ctx.author.id)] = {
            "userID": str(ctx.author.id),
            "hours": 12,
            "msgID": msg.id
        }
        
        r['general'].append(ctx.author.id)
        
    
    if forwhat == "Client":
        embed = discord.Embed()
        embed.title = "Physiological Client Queue"
        embed.description = f"You are now in the queue. I will ping you again when your key is ready.\nRemaining hours: **12h**"
        embed.color = discord.Color.blurple()
        embed.set_footer(text="You can buy to get a key instantly!")
    
        msg = await ctx.author.send(embed=embed)
    
        r['client']['users'][str(ctx.author.id)] = {
            "userID": str(ctx.author.id),
            "hours": 12,
            "msgID": msg.id
        }
        
        r['general'].append(str(ctx.author.id))
    
    with open('settings.json', 'w') as f:
        json.dump(r, f)

@tasks.loop(hours=1)
async def keymanager():
    try:
        with open('settings.json', 'r') as f:
            r = json.load(f)

        ids = r['general']
        users = []

        for id in ids:
            users.append(id)

        for user in users:
            try:
                usr = bot.get_user(int(user))

                if usr.dm_channel is None:
                    await usr.create_dm()

                ch = usr.dm_channel
                msg = await ch.history(limit=1).flatten()

                if len(msg) > 0:
                    msg = msg[0]

                    if msg.embeds[0].title == "Physiological Clicker Queue":
                        missing = r['clicker']['users'][str(user)]['hours']
                        missing -= 1

                        if missing == 0:
                            embed = discord.Embed()
                            embed.title = "**Your Clicker key is ready!**"
                            embed.description = f"Please click the button down here to get your key."
                            embed.color = discord.Color.brand_green()
                            rht = random.randint(0, 999999)
                            bnt = discord.ui.Button(
                                label="🔑 Get your key",
                                style=discord.ButtonStyle.url,
                                url=f"http://127.0.0.1:27123/verify?code={rht}&userID={usr.id}&type=client"
                            )
                            view = discord.ui.View()
                            view.add_item(bnt)
                            await usr.send(embed=embed, view=view)
                            del r['clicker']['users'][str(user)]
                            r['clicker']['timeouts'][str(user)] = {'time': 8}
                            r['verificationcodes'][rht] = {'ownerID': usr.id}

                        new = discord.Embed()
                        new.title = "Physiological Clicker Queue"
                        new.description = f"You are now in the queue. I will ping you again when your key is ready.\nRemaining hours: **{missing}h**"
                        new.color = discord.Color.blurple()
                        new.set_footer(text="You can buy to get a key instantly!")

                        await msg.edit(content=None, embed=new)

                        if missing > 0:
                            r['clicker']['users'][str(user)]['hours'] = missing

                    elif msg.embeds[0].title == "Physiological Client Queue":
                        missing = r['client']['users'][str(user)]['hours']
                        missing -= 1

                        if missing == 0:
                            embed = discord.Embed()
                            embed.title = "**Your Client key is ready!**"
                            embed.description = f"Please click the button down here to get your key."
                            embed.color = discord.Color.brand_green()
                            rht = random.randint(0, 999999)
                            bnt = discord.ui.Button(
                                label="🔑 Get your key",
                                style=discord.ButtonStyle.url,
                                url=f"http://127.0.0.1:27123/verify?code={rht}&userID={usr.id}&type=client"
                            )
                            view = discord.ui.View()
                            view.add_item(bnt)
                            await usr.send(embed=embed, view=view)
                            del r['client']['users'][str(user)]
                            r['client']['timeouts'][str(user)] = {'time': 8}
                            r['verificationcodes'][rht] = {'ownerID': usr.id}
                            with open('settings.json', 'w') as f:
                                json.dump(r, f)

                            
                        new = discord.Embed()
                        new.title = "Physiological Client Queue"
                        new.description = f"You are now in the queue. I will ping you again when your key is ready.\nRemaining hours: **{missing}h**"
                        new.color = discord.Color.blurple()
                        new.set_footer(text="You can buy to get a key instantly!")

                        await msg.edit(content=None, embed=new)

                        if missing > 0:
                            r['client']['users'][str(user)]['hours'] = missing
                else:
                    if str(user) in r['clicker']['users']:
                        del r['clicker']['users'][str(user)]
                    if str(user) in r['client']['users']:
                        del r['client']['users'][str(user)]
                    with open('settings.json', 'w') as f:
                        json.dump(r, f)

            except Exception as e:
                print(e)

        with open('settings.json', 'w') as f:
            json.dump(r, f)
    except Exception as e:
        print(e)



@tasks.loop(hours=24)
async def timeout():
    with open('settings.json', 'r') as f:
        r = json.load(f)
    
    inTimeoutClicker = r['clicker']['timeouts'].keys()
    inTimeoutClient = r['client']['timeouts'].keys()
    
    for y in inTimeoutClicker:
       
        missing = r['clicker']['timeouts'][y]['time']
        missing -= 1
                
        if missing == 0:
          
            del r['clicker']['timeouts'][y]

            with open('settings.json', 'w') as f:
                json.dump(r, f)
        
        try: r['clicker']['timeouts'][str(y)]['time'] = missing
        except: pass    
        
        with open('settings.json', 'w') as f:
            json.dump(r, f)
    
    for y in inTimeoutClient:
       
        missing = r['client']['timeouts'][str(y)]['time']
        missing -= 1
                
        if missing == 0:
          
            del r['client']['timeouts'][y]

            with open('settings.json', 'w') as f:
                json.dump(r, f)
        
        try: r['client']['timeouts'][y]['time'] = missing
        except: pass   
        
        with open('settings.json', 'w') as f:
            json.dump(r, f)

@bot.event
async def on_ready():
    print('OK')
    #! Start key managers
    keymanager.start()
    timeout.start()
    
    while True:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name='Minecraft'))
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name='Minecraft with Physiological'))
        await asyncio.sleep(10)


#! FLASK CODE

app = quart.Quart(__name__)

@app.route('/')
async def home():
    return 'Some random API.'

@app.route('/verify', methods=['GET'])
async def verification():
    
    with open('settings.json', 'r') as gas:
        gaf = json.load(gas)
    
    try:
        code = quart.request.args.get('code')
        userID = quart.request.args.get('userID')
        print(userID)
    except:
        print('Code or userID check not passed.')
        return {'status': 'error', 'message': 'Validation error.'}

    try:
        guild = bot.get_guild(925899906655326249)
        usr = guild.get_member(int(userID))
        print("Verification check: {}".format(usr.id))
    except: return {'status': 'error', 'message': 'Validation error.'}

    with open('settings.json', 'r') as f:
        r = json.load(f)

    try:
        thing = r['verificationcodes'].keys()
        for x in thing:
            if str(x) == str(code):
                if r['verificationcodes'][str(code)]['ownerID'] == userID:
                    return {'status': 'error', 'message': 'Validation error.'}
    except:
        print('Verification code check not passed.')
        return {'status': 'error', 'message': 'Validation error.'}

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    response = requests.get(f"https://api.ipify.org?format=json&ip={user_ip}")
    data = response.json()
    ip = data['ip']
    
    key = requests.get(config['keys'][quart.request.args.get('type')]['1week']['URL'])
        
    embed = discord.Embed()
    embed.title = "**Verification**"
    embed.color = discord.Color.brand_green()
    embed.description = f"IP: `{ip}`\nStatus: Verification passed\nUser: {usr.mention}"
    embed.set_footer(text='Powered by ipify')

    
    ch = bot.get_channel(1126565540161409126)
    await ch.send(embed=embed)
    if usr.dm_channel is None:
            await usr.create_dm()

    ch2 = usr.dm_channel

    new = discord.Embed()
    new.title = "**Key**"
    new.color = discord.Color.blue()
    new.description = f"Here is your key: ||`{key.text}`||"
    try: del r["verificationcodes"][str(code)]; await usr.send(embed=new)
    except: return { 'status': 'error' }
    
        
    try:
        if int(usr.id) in r['general']:
            r['general'].remove(int(usr.id))
    except:
        if str(usr.id) in r['general']:
            r['general'].remove(str(usr.id))
        
    with open('settings.json', 'w') as f:
        json.dump(r, f)
        
    return "Verified with success. Go back to Discord to get your key."


#def run_server():
#    
    

#def verification_server():
#    server_thread = threading.Thread(target=run_server)
#    server_thread.start()

#verification_server()
bot.loop.create_task(app.run_task(host="0.0.0.0", port=27123))
bot.run(config['token'])
