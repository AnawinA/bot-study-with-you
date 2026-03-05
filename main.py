import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.environ["Token"]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} Activated")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first 😅")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client:
        await ctx.send("I'm already here!")
        return

    await channel.connect()
    await ctx.send("Joined the voice channel 🎧")

@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel 🤔")
        return

    await ctx.voice_client.disconnect()
    await ctx.send("Left the voice channel 👋")

keep_alive()
bot.run(TOKEN)