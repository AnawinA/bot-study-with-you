import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(f"Loading IDs... Voice: {os.getenv('WORK_VOICE_CHANNEL')}, Text: {os.getenv('WORK_CHANNEL')}")
try:
    WORK_VOICE_CHANNEL_ID = int(os.getenv('WORK_VOICE_CHANNEL'))
    WORK_CHANNEL_ID = int(os.getenv('WORK_CHANNEL'))
    CATEGORY_ID = os.getenv('CATEGORY_ID') # Optional, currently unused but requested to be in .env
except (TypeError, ValueError):
    print("Error: WORK_VOICE_CHANNEL or WORK_CHANNEL not set correctly in .env")
    WORK_VOICE_CHANNEL_ID = 0
    WORK_CHANNEL_ID = 0

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

class StudyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} slash commands for {self.user}")

bot = StudyBot()

# Message data
GREETINGS_A = ["Oh hey!", "Hi there!", "Welcome welcome! 👋", "Work mode activated 💼😄", "Heyyy,", "Nice to see you here! 🌱", "Oh!", "Looks like a productive moment 💡", "Hi hi!", "Welcome to the work zone! 🚀"]
GREETINGS_B = ["You came to work 😊 Want some company? Use /studywithme and I’ll join you!", "Focus time already? ✨ Type /studywithme and we can work together!", "If you’d like a study buddy, just use /studywithme!", "Use /studywithme and I’ll hop into the voice chat!", "time to get things done? 📚 Use /studywithme and I’ll join you right away!", "If you want me around, use /studywithme!", "A new worker appeared 👀✨ Run /studywithme and let’s focus together!", "Use /studywithme and I’ll keep you company!", "Ready to work? 😄 Just type /studywithme and I’ll join in!", "Use /studywithme and let’s stay focused together!"]

READY_NOT_JOINED_A = ["I’m already here! 😊", "I’m here already 👋", "Yep, I’m here! �", "I’m right here 👀✨", "Already standing by! 🚀", "I’m here and ready 💼😊", "Hi hi, I’m already here 😆", "I’m here! 🌱", "Already here 👋😄", "I’m here and prepared ✨"]
READY_NOT_JOINED_B = ["Just say the word and I’ll jump in!", "Ready whenever you are!", "Let me know if you want to start!", "Waiting for you!", "Just tell me when!", "Let’s do this!", "Shall we begin?", "Ready to focus together!", "Let’s get to work!", "Whenever you’re ready!"]

READY_ALREADY_JOINED_A = ["I’m already here 😅", "I’m here already 👀", "Yep, I’m here 😄", "Still here! 😊", "I’m here with you 🎧", "I never left 😅", "I’m already in the channel 👋😄", "Here I am! ✨", "I’m here and listening 🎧😊", "Already here 😄"]
READY_ALREADY_JOINED_B = ["Right beside you!", "Didn’t go anywhere!", "Let’s keep going!", "Ready to continue!", "Let’s stay focused!", "I’m right here!", "Let’s work!", "Still studying with you!", "Let’s do our best!", "Let’s keep the momentum!"]

FOLLOW_MESSAGES_A = ["You can go first 😊", "Go ahead! 👋", "No worries 😄", "You lead the way 🚶‍♂️✨", "Go on first 😊", "Sounds good 👍😄", "You can start first 🌱", "Alright! 😊", "Go ahead 🚀", "You first �"]
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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Set the bot's activity status
    await bot.change_presence(activity=discord.Game(name="Studying 📚"))
    print("Status set to 'Studying'")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    # Someone joined a voice channel
    if after.channel:
        # Check if they joined the SPECIFIC work channel for the greeting
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
            # Check if bot is in the channel that just became empty
            if vc and vc.channel.id == before.channel.id:
                print(f"Leaving empty channel: {before.channel.name}")
                await vc.disconnect()
                channel = bot.get_channel(WORK_CHANNEL_ID)
                if channel:
                    msg = f"{random.choice(GOODBYE_PART_A)}, {random.choice(GOODBYE_PART_B)}"
                    await channel.send(msg)

@bot.tree.command(name="studywithme", description="Study with the bot!")
async def studywithme(interaction: discord.Interaction):
    print(f"Command /studywithme used by {interaction.user}")
    
    if interaction.user.voice:
        voice_channel = interaction.user.voice.channel
        print(f"User is in voice channel: {voice_channel.name} ({voice_channel.id})")
        
        vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        
        gif_file = "working.gif"
        if not os.path.exists(gif_file):
            if os.path.exists("reading.gif"):
                gif_file = "reading.gif"
            else:
                gif_file = None

        if vc and vc.is_connected():
            if vc.channel.id == voice_channel.id:
                print("Bot already in the same channel.")
                response = f"{random.choice(READY_ALREADY_JOINED_A)} {random.choice(READY_ALREADY_JOINED_B)}"
            else:
                print(f"Moving from {vc.channel.name} to {voice_channel.name}")
                response = f"{random.choice(READY_NOT_JOINED_A)} {random.choice(READY_NOT_JOINED_B)}"
                await vc.move_to(voice_channel)
            await interaction.response.send_message(response)
        else:
            print(f"Attempting to join channel: {voice_channel.name}")
            response = f"{random.choice(READY_NOT_JOINED_A)} {random.choice(READY_NOT_JOINED_B)}"
            await interaction.response.send_message(response)
            try:
                await voice_channel.connect()
                print("Successfully joined voice channel!")
            except Exception as e:
                print(f"CRITICAL ERROR - Failed to connect: {e}")
    else:
        print("User is not in any voice channel.")
        msg = f"{random.choice(FOLLOW_MESSAGES_A)} {random.choice(FOLLOW_MESSAGES_B)}"
        await interaction.response.send_message(msg)

    # Send GIF if it exists
    if gif_file := (locals().get('gif_file')): # Safely check if gif_file exists in scope
        if gif_file:
            await interaction.channel.send(file=discord.File(gif_file))

@bot.tree.command(name="ping", description="Check the bot's latency!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 Latency: {round(bot.latency * 1000)}ms")

@bot.tree.command(name="greet", description="Get a friendly greeting!")
async def greet(interaction: discord.Interaction):
    msg = f"{random.choice(GREETINGS_A)} {random.choice(GREETINGS_B)}"
    await interaction.response.send_message(msg)

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in .env")
