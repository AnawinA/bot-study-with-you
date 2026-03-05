import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "YOUR_BOT_TOKEN_HERE"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    # User not in voice channel
    if not interaction.user.voice:
        await interaction.response.send_message(
            "❌ You must be in a voice channel first!",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    # Already connected
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
        await interaction.response.send_message(
            f"🔁 Moved to **{channel.name}**"
        )
    else:
        await channel.connect()
        await interaction.response.send_message(
            f"🔊 Joined **{channel.name}**"
        )


@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if not voice_client:
        await interaction.response.send_message(
            "❌ I'm not in a voice channel.",
            ephemeral=True
        )
        return

    await voice_client.disconnect()
    await interaction.response.send_message("👋 Left the voice channel")

if __name__ == "__main__":
    if TOKEN:
        keep_alive()
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in .env")
