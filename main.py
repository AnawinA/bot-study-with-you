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
GREETINGS = ["", "", "Hello!", "Oh heyy!", "Hi there!", "Welcome!", "Work mode activated 🔥", "Heyyy,", "Nice to see you here,", "Oh,", "A productive moment!", "Hi hi!", "You're here,", "You came to work!", "Focus time already?", "A new worker appeared ✨", "Ready to work"]

MSG_SPACE = [" ", " ", ", ", "! ", "!", "- ", ". "]

ASK_TO_JOIN = [
    "Want some company?",
    "Can we work together? 🥺",
    "Wanna work together?",
    "I'm free to join the VC if you'd like company! ✨",
    "Would you like to work together?",
    "Can I jump in with you?\nTotally okay if you're in the zone! 🎧",
    "I can join in if you want someone there!",
    "If you want someone there! I can join in",
    "Should I pop in?\nI'm happy to just hang out if it helps! 👋",
    "Want to work together?\nI'm around if you want me to join!",
    "Do you want me to hop in the voice chat?",
    "Should I join you in there?",
    "Want to study together? I can join!",
    "Do you want me to jump in the VC with you?"
]

# hidden messages (Only first person can see this) after ask to join
ASK_TO_JOIN_HIDDEN = "-# • `hito join` to join your voice channel 😊\n-# • `hito whatru` to ask me what am I doing?\n-# • Start Pomodoro at <#1478989487332655245>"

# old = READY_NOT_JOINED_A
JOINED_A_OPTIONAL = ["I’m already here", "I’m here already", "Yep, I’m here", "I’m right here ✨", "Already standing by", "I’m here and ready", "Hi hi, I’m already here", "I’m here", "Already here", "I’m here and prepared ✨"]

JOINED_B = ["Let's go!", "Let's start!", "Let's focus!", "Let's work!", "Let's study!", "Let's do this!", "Let's begin!", "Let's get to work!", "Let's keep going!", "Let's stay focused!", "Time to focus!", "Ready to get some work done!", "Focus mode: ON!", "Ready to start!", "Time to get productive!", "Ready for a productive session!"]

# hidden messages  (Only someone make hito join can see this) after joined
JOINED_HIDDEN = "-# • `hito leave` to leave the voice channel\n-# • /timer = Check Pomodoro or at <#1478989487332655245>\n-# • /now <tag> = set whate are you doing, /clear"

READY_ALREADY_JOINED_A = ["I’m already here", "I’m here already", "Yep, I’m here", "Still here", "I’m here with you", "I never left", "I’m already in the channel", "Here I am", "I’m here and listening", "Already here"]
READY_ALREADY_JOINED_B_OPTIONAL = ["Right beside you!", "Didn’t go anywhere!", "Let’s keep going!", "Ready to continue!", "Let’s stay focused!", "I’m right here!", "Let’s work!", "Still studying with you!", "Let’s do our best!", "Let’s keep the momentum!"]

FOLLOW_MESSAGES_A_OPTIONAL = ["You can go first", "Go ahead!", "No worries", "You lead the way", "Go on first", "Sounds good", "You can start first", "Alright!", "Go ahead", "You first"]
FOLLOW_MESSAGES_B = ["I’ll join you right away!", "I’ll follow you in a moment!", "I’ll join as soon as you’re there!", "I’ll join you right after!", "I’ll be there in no time!", "I’ll join you shortly!", "I’ll join you right away!", "I’ll meet you there soon!", "I’ll join once you’re ready!", "I’ll catch up immediately!"]


WHAT_DO_YOU_DO_A = [
    "I'm reading a book", "I'm reading a manga", "I'm working on a project", 
    "I'm studying", "I'm coding", "I'm organizing my tasks", "I'm reviewing my notes", 
    "I'm writing some documentation", "I'm planning my week", "I'm doing some research", 
    "I'm practicing some skills", "I'm catching up on emails", "I'm sketching some ideas", 
    "I'm listening to focus music"
]

ASK_BACK = [
    "and you?", "how about you?", "what about you?", "what are you up to?", 
    "what are you working on?", "how about yourself?", "and yourself?", 
    "what's on your list today?", "what are you focusing on?", "what are you studying?", 
    "what's your plan?", "what are you doing?", "what's your focus for today?", 
    "what are you planning to do?", "what's on your mind?"
]


GOODBYE_PART_A = [
    "Thank you for inviting me", "That was a nice session", "I enjoyed studying together",
    "That was productive", "I’m glad I could join", "Thanks for having me here",
    "That was a good focus time", "I appreciate the time together", "It was fun working together",
    "I’m happy I could help"
]

GOODBYE_PART_B_OPTIONAL = [
    "see you next time!", "see you later!", "see you soon!", "catch you next time!",
    "talk to you again soon!", "hope we study again soon!", "good luck with your work!",
    "take care!", "have a great rest of your day!", "don't forget to rest!"
]

def get_random_message(list_a, list_b, use_msg_space=False, opt_a=False, opt_b=False):
    a = random.choice(list_a) if list_a else ""
    if opt_a and random.random() < 0.5:
        a = ""
    
    b = random.choice(list_b) if list_b else ""
    if opt_b and random.random() < 0.5:
        b = ""
        
    if not a: return b
    if not b: return a
    
    sep = random.choice(MSG_SPACE) if use_msg_space else " "
    return f"{a}{sep}{b}"


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
        msg = get_random_message(GREETINGS, ASK_TO_JOIN, use_msg_space=True)
        msg += f"\n{ASK_TO_JOIN_HIDDEN}"
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
                    msg = get_random_message(GREETINGS, ASK_TO_JOIN, use_msg_space=True)
                    msg += f"\n{ASK_TO_JOIN_HIDDEN}"
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
                    msg = get_random_message(GOODBYE_PART_A, GOODBYE_PART_B_OPTIONAL, use_msg_space=True, opt_b=True)
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
                response = get_random_message(READY_ALREADY_JOINED_A, READY_ALREADY_JOINED_B_OPTIONAL, use_msg_space=True, opt_b=True)
                response += f"\n{JOINED_HIDDEN}"
            else:
                response = get_random_message(JOINED_A_OPTIONAL, JOINED_B, use_msg_space=False, opt_a=True)
                response += f"\n{JOINED_HIDDEN}"
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
                response = get_random_message(JOINED_A_OPTIONAL, JOINED_B, use_msg_space=False, opt_a=True)
                response += f"\n{JOINED_HIDDEN}"
                await ctx.send(response)
            except Exception as e:
                await ctx.send(f"I tried to join, but I ran into an error: `{e}`. Make sure I have 'PyNaCl' and 'davey' installed! 😅")
                return
    else:
        msg = get_random_message(FOLLOW_MESSAGES_A_OPTIONAL, FOLLOW_MESSAGES_B, use_msg_space=False, opt_a=True)
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
    msg = get_random_message(GREETINGS, ASK_TO_JOIN, use_msg_space=True)
    msg += f"\n{ASK_TO_JOIN_HIDDEN}"
    await ctx.send(msg)

@bot.command()
async def join(ctx):
    # Alias to studywithme or simplified join
    await studywithme(ctx)

@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel 😅")
        return

    await ctx.voice_client.disconnect()
    msg = get_random_message(GOODBYE_PART_A, GOODBYE_PART_B_OPTIONAL, use_msg_space=True, opt_b=True)
    await ctx.send(msg)

@bot.command(name="whatru")
async def whatru(ctx):
    msg = f"{random.choice(WHAT_DO_YOU_DO_A)}, {random.choice(ASK_BACK)}"
    await ctx.send(msg)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)


