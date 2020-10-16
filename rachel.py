import sys
import re
import os
from math import *
import random as rand
import json
import urllib.error
from urllib.request import urlopen
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from datetime import datetime
import praw

with open('tokens.txt') as f:
    tokens = f.read().splitlines()

#line 0 = discord api
#line 1 = finnhub api
#line 2 = reddit id
#line 3 = reddit secret

client = Bot(command_prefix = "$")

reddit = praw.Reddit(client_id = tokens[2], client_secret = tokens[3], user_agent = "rachelbot")

#helpers
def imgtostring(l, s):
    outstr = "```fix\n"

    for line in l:
        for i in range(floor(len(s)/2) + 1):
            outstr += line.replace('o', (' ' * len(s))).replace('x', s).replace('    ', '\t') + '\n'
            
    outstr += "```"
    return outstr

def ismod(user):
    for role in user.roles:
        if (role.name == "mod"):
            return True
    return False
    
def msgtostring(*strs):
    st = ''
    for s in strs:
        st += s + ' '
    
    return st
    
    
#events
@client.event
async def on_ready():
    try:
        client.add_cog(Mod(client))
        client.add_cog(AmongUs(client))
        client.add_cog(General(client))
        print("All cogs loaded")    
    except discord.ext.commands.errors.CommandRegistrationError:
        print("Failed to load one or more cogs, they may already be loaded")
    
    with open('status.txt') as s:
        status = s.readline()
    
    await client.change_presence(activity=discord.Game(name=status))
    
    print("Ready")
    
@client.event
async def on_message(message):
    if not os.path.exists(os.path.join("users", str(message.author.id))):
        os.makedirs(os.path.join("users", str(message.author.id)))

    record = "{}#{} at {} UTC in {} - #{}".format(message.author.name, message.author.discriminator, str(datetime.utcnow()), message.guild.name, message.channel.name)

    with open(os.path.join("users", str(message.author.id), "history.txt"), 'a') as userlog:
        userlog.write("<<{}>> {}\n".format(record, message.content))
    try:
        if message.content[0] == '$':
            print(record + ": " + message.content)
            with open('log.txt', 'a') as l:
                l.write("<<{}>> {}\n".format(record, message.content))
    except IndexError:
        pass
        
    await client.process_commands(message)


#Mod commands
class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(brief = "Kills the bot (mod only)")
    async def kill(self, ctx):
        if ismod(ctx.author):
            await ctx.send("Goodbye!")
            await client.close()
            exit(0)
        
        await ctx.send("You don't have that permission")
        
    @commands.command(brief = "Change currently playing (mod only)")
    async def playing(self, ctx, *string):
        if ismod(ctx.author):
            await client.change_presence(activity=discord.Game(name=msgtostring(*string)))
            with open('status.txt', 'w') as s:
                s.write(msgtostring(*string))
        
            await ctx.send("Done!")
        else:
            await ctx.send("You don't have that permission")
    

#Among us commands
class AmongUs(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.deadlist = []
        
    async def setmutestatus(self, ctx, status): #global mute or unmute voice channel
        chan = ctx.author.voice.channel
    
        if ismod(ctx.author):
            for member in chan.members:
                await member.edit(mute = status)
        else:
            await ctx.send("You don't have that permission")
    
    @commands.command(brief = "Mute everyone in voice channel (mod only)")
    async def m(self, ctx):
        await self.setmutestatus(ctx, True)
    
    @commands.command(brief = "Unmutes everyone in voice channel (mod only)")
    async def um(self, ctx):
        chan = ctx.author.voice.channel
    
        if ismod(ctx.author):
            for member in chan.members:
                if member not in self.deadlist:
                    await member.edit(mute = False)
        else:
            await ctx.send("You don't have that permission")
    
    @commands.command(brief = "Declare a player as dead (mod only)")
    async def dead(self, ctx, *users: discord.User):
        chan = ctx.author.voice.channel

        if ismod(ctx.author):
            for member in chan.members:
                if member in users:
                    self.deadlist.append(member)
                    await member.edit(mute = True)

        else:
            await ctx.send("You don't have that permission")

    @commands.command(brief = "End the game (mod only)")
    async def eg(self, ctx):
        await self.setmutestatus(ctx, False)
        self.deadlist.clear()


#general commands
class General(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(brief = "Pings the bot")
    async def ping(self, ctx):
        await ctx.send("hello!")

    @commands.command(brief = "Ask a question")
    async def ask(self, ctx, *string):
        if (ctx.author.id == 261630719132958720):
            if "do you love me" in msgtostring(*string):
                await ctx.send("only you bb")
                return
                
            elif "wanna smash" in msgtostring(*string):
                await ctx.send("destroy my RAM sticks bb")
                return
            
        def answer(argument):
            switcher = {
                1: "yes",
                2: "totally",
                3: "no",
                4: "nah",
                5: "maybe",
                6: "I'm not sure"
            }
            return switcher.get(argument, "I don't know")
        await ctx.send(answer(rand.randint(1,6)))
    
    @commands.command(brief = "Choose between multiple things")
    async def pick(self, ctx, *string):
        choicelist = []
        i = 0
        
        choicelist.append("")
        
        for s in string:
            if s == "or":
                choicelist.append("")
                i += 1
            else: 
                choicelist[i] += (s + ' ')
        
        await ctx.send(choicelist[rand.randint(0, i)])
        
    @commands.command(brief = "Tell a joke")
    async def joke(self, ctx):
        jokelist = []
        
        for post in reddit.subreddit("jokes").new(limit = 100):
            if (len(post.selftext) <= 300):
                jokelist.append("{} {}".format(post.title, post.selftext))

        await ctx.send(jokelist[rand.randint(0, len(jokelist) - 1)])
        
    @commands.command(brief = "Quick maths")
    async def math(self, ctx, *string):
        expr = ''
        for s in string:
            expr += s
        
        expr = expr.replace("^", "**")
        
        #print(expr)
        
        try:
            await ctx.send(eval(expr, {'__builtins__': None}, {'pi':pi, 'e':e, 'sqrt':sqrt, 'cos':cos, 'sin':sin, 'tan':tan, 'fact':factorial}))
        except (TypeError, SyntaxError):
            await ctx.send("Invalid expression")
        except OverflowError:
            await ctx.send("Result is too large")
        
    @commands.command(brief = "Stock prices for big ballers like Jaime")
    async def stonks(self, ctx, symbol):
        query = "https://finnhub.io/api/v1/quote?symbol={}&token={}".format(symbol, tokens[1])
        data = json.loads(urlopen(query).read())
        
        emote = ''
        sign = ''
        
        if (data['c'] > data['pc']):
            emote = '\U0001F4C8'
            sign = '+'
        else:
            emote = '\U0001F4C9'
            sign = ''
        
        pct = (float(data['c'] - data['pc']) / float(data['c'])) * 100
        
        await ctx.send("{}: {} | {}{:0.2f} ({:0.2f}%) {}".format(symbol, str(data['c']), sign, float(data['c'] - data['pc']), pct, emote))
        
    @commands.command(brief = "\U0001F5FF \U0001F4DC \U00002702\U0000FE0F")
    async def rps(self, ctx, usr_choice):
        choices = ["rock", "paper", "scissors"]

        bot_choice = rand.randint(0, 2) 
        
        await ctx.send("**You Chose:** {0}\n**I Chose:** {1}".format(usr_choice.lower(), choices[bot_choice]))
        
        try:
            outcome = choices.index(usr_choice) - bot_choice
            if outcome == 0:
                result = "tie"
            elif outcome == -1 or outcome == 2:
                result = "lose"
            else:
                result = "win"
            
            await ctx.send("*You {0}*".format(result))
            
        except ValueError:
            await ctx.send("*invalid input*")
            

print("Starting bot...")
client.run(tokens[0])