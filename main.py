import os
import random
import asyncio
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Flask server to keep the bot alive
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# Configuration
TOKEN = os.getenv("DISCORD_TOKEN")
try:
    WORK_VOICE_CHANNEL_ID = int(os.getenv('WORK_VOICE_CHANNEL', 0))
    WORK_CHANNEL_ID = int(os.getenv('WORK_CHANNEL', 0))
    CATEGORY_ID = os.getenv('CATEGORY_ID')
except (TypeError, ValueError):
    print("Error: WORK_VOICE_CHANNEL or WORK_CHANNEL not set correctly in .env")
    WORK_VOICE_CHANNEL_ID = 0
    WORK_CHANNEL_ID = 0

# Message data
GREETINGS_A = ["Oh hey!", "Hi there!", "Welcome welcome! 👋", "Work mode activated 💼😄", "Heyyy,", "Nice to see you here! 🌱", "Oh!", "Looks like a productive moment 💡", "Hi hi!", "Welcome to the work zone! 🚀"]
GREETINGS_B = [
    "You came to work 😊 Want some company? Use hito studywithme and I’ll join you!",
    "Focus time already? ✨ Type hito studywithme and we can work together!",
    "If you’d like a study buddy, just use hito studywithme!",
    "Use hito studywithme and I’ll hop into the voice chat!",
    "time to get things done? 📚 Use hito studywithme and I’ll join you right away!",
    "If you want me around, use hito studywithme!",
    "A new worker appeared 👀✨ Run hito studywithme and let’s focus together!",
    "Use hito studywithme and I’ll keep you company!",
    "Ready to work? 😄 Just type hito studywithme and I’ll join in!",
    "Use hito studywithme and let’s stay focused together!"
]

READY_NOT_JOINED_A = ["I’m already here! 😊", "I’m here already 👋", "Yep, I’m here!  ", "I’m right here 👀✨", "Already standing by! 🚀", "I’m here and ready 💼😊", "Hi hi, I’m already here!", "I’m here! 🌱", "Already here 👋😄", "I’m here and prepared ✨"]
READY_NOT_JOINED_B = ["Just say the word and I’ll jump in!", "Ready whenever you are!", "Let me know if you want to start!", "Waiting for you!", "Just tell me when!", "Let’s do this!", "Shall we begin?", "Ready to focus together!", "Let’s get to work!", "Whenever you’re ready!"]

READY_ALREADY_JOINED_A = ["I’m already here 😅", "I’m here already 👀", "Yep, I’m here 😄", "Still here! 😊", "I’m here with you 🎧", "I never left 😅", "I’m already in the channel 👋😄", "Here I am! ✨", "I’m here and listening 🎧😊", "Already here 😄"]
READY_ALREADY_JOINED_B = ["Right beside you!", "Didn’t go anywhere!", "Let’s keep going!", "Ready to continue!", "Let’s stay focused!", "I’m right here!", "Let’s work!", "Still studying with you!", "Let’s do our best!", "Let’s keep the momentum!"]

FOLLOW_MESSAGES_A = ["You can go first 😊", "Go ahead! 👋", "No worries 😄", "You lead the way 🚶♂️✨", "Go on first 😊", "Sounds good 👍😄", "You can start first 🌱", "Alright! 😊", "Go ahead 🚀", "You first  "]
FOLLOW_MESSAGES_B = ["I’ll join you right away!", "I’ll follow you in a moment!", "I’ll join as soon as you’re there!", "I’ll join you right after!", "I’ll be there in no time!", "I’ll join you shortly!", "I’ll join you right away!", "I’ll meet you there soon!", "I’ll join once you’re ready!", "I’ll catch up immediately!"]

GOODBYE_PART_A = [
    "Thank you for inviting me", "That was a nice session", "I enjoyed studying together",
    "That was productive", "I’m glad I could join", "Thanks for having me here",
    "That was a good focus time", "I appreciate the time together", "It was fun working together",
    "I’m happy I could help"
]

GOODBYE_PART_B = [
    "see you next time!", "see you later!", "see you soon!", "catch you next time!",
    "talk to you again soon!", "hope we study again soon!", "good luck with your work!",
    "take care!", "have a great rest of your day!", "don't forget to rest!"
]

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

# Prefix is 'hito ' (case insensitive)
bot = commands.Bot(command_prefix=["hito ", "Hito "], intents=intents, case_insensitive=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
        
    # If the message is just 'hito' (case insensitive), send a greeting
    if message.content.lower().strip() == "hito":
        msg = f"{random.choice(GREETINGS_A)} {random.choice(GREETINGS_B)}"
        await message.channel.send(msg)
        return
        
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Studying 📚"))
    
    if not discord.opus.is_loaded():
        print("Opus library not loaded. Voice support might be unstable.")
    
    print("Bot is ready and Status is set to 'Studying'")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    # Someone joined a voice channel
    if after.channel:
        if after.channel.id == WORK_VOICE_CHANNEL_ID and (before.channel is None or before.channel.id != WORK_VOICE_CHANNEL_ID):
            members = [m for m in after.channel.members if not m.bot]
            if len(members) == 1:
                channel = bot.get_channel(WORK_CHANNEL_ID)
                if channel:
                    msg = f"{random.choice(GREETINGS_A)} {random.choice(GREETINGS_B)}"
                    await channel.send(msg)

    # Someone left a voice channel
    if before.channel:
        remaining_members = [m for m in before.channel.members if not m.bot]
        if len(remaining_members) == 0:
            vc = discord.utils.get(bot.voice_clients, guild=member.guild)
            if vc and vc.channel.id == before.channel.id:
                print(f"Leaving empty channel: {before.channel.name}")
                await vc.disconnect()
                channel = bot.get_channel(WORK_CHANNEL_ID)
                if channel:
                    msg = f"{random.choice(GOODBYE_PART_A)}, {random.choice(GOODBYE_PART_B)}"
                    await channel.send(msg)

@bot.command(name="studywithme")
async def studywithme(ctx):
    print(f"Command hito studywithme used by {ctx.author}")
    
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
        vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        
        gif_file = "reading.gif" if os.path.exists("reading.gif") else None

        if vc and vc.is_connected():
            if vc.channel.id == voice_channel.id:
                response = f"{random.choice(READY_ALREADY_JOINED_A)} {random.choice(READY_ALREADY_JOINED_B)}"
            else:
                response = f"{random.choice(READY_NOT_JOINED_A)} {random.choice(READY_NOT_JOINED_B)}"
                try:
                    await vc.move_to(voice_channel)
                except Exception as e:
                    response = f"I tried to move to you, but something went wrong: {e} 😅"
            await ctx.send(response)
        else:
            try:
                # Check permissions
                permissions = voice_channel.permissions_for(ctx.guild.me)
                if not permissions.connect or not permissions.speak:
                    await ctx.send("Oh! I don't have permission to join or speak in that channel. Could you check my roles? 🥺")
                    return

                await voice_channel.connect(timeout=20, reconnect=True, self_deaf=True, self_mute=True)
                response = f"{random.choice(READY_NOT_JOINED_A)} {random.choice(READY_NOT_JOINED_B)}"
                await ctx.send(response)
            except Exception as e:
                await ctx.send(f"I tried to join, but I ran into an error: `{e}`. Make sure I have 'PyNaCl' and 'davey' installed! 😅")
                return
    else:
        msg = f"{random.choice(FOLLOW_MESSAGES_A)} {random.choice(FOLLOW_MESSAGES_B)}"
        await ctx.send(msg)

    # Ensure status is set to Studying
    await bot.change_presence(activity=discord.Game(name="Studying 📚"))

    if gif_file:
        await ctx.send(file=discord.File(gif_file))

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 Latency: {round(bot.latency * 1000)}ms")

@bot.command(name="greet")
async def greet(ctx):
    msg = f"{random.choice(GREETINGS_A)} {random.choice(GREETINGS_B)}"
    await ctx.send(msg)

@bot.command()
async def join(ctx):
    # Alias to studywithme or simplified join
    await studywithme(ctx)

@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel 🤔")
        return

    await ctx.voice_client.disconnect()
    await ctx.send("Left the voice channel 👋")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)


