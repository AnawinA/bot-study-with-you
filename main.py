import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Syncs slash commands with Discord
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.tree.command(name="join", description="Joins your current voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Joined **{channel.name}**!")
    else:
        await interaction.response.send_message("You need to be in a voice channel first!", ephemeral=True)

@bot.tree.command(name="leave", description="Leaves the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("I've left the voice channel.")
    else:
        await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)

bot.run(TOKEN)