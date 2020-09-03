import discord

client = discord.ext.commands.Bot(command_prefix = "$")

@client.command(brief="description")
async def hello(ctx):
    #stuff you want it to do

client.run("d28m3hfuagyufag67tgweq768rf")