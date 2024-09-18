import os
import random
import discord
from discord.ext import commands
from discord.ui import Button, View
from server import server_on

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# Function to generate a random number for the links
def generate_random_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

# Function to generate URLs with random numbers attached
def generate_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/",
        "https://www.facebook.com/groups/289008456634964/",
        "https://www.facebook.com/groups/fivemthailandcommunity/"
    ]

    generated_links = []
    for link in links:
        random_number = generate_random_number()
        full_link = link + random_number
        generated_links.append(full_link)
    return generated_links

# Dictionary to track button press cooldowns for each user
cooldowns = {}

# Persistent View class with a button and custom_id for persistence
class MyPersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view, never times out

    @discord.ui.button(label="Generate URLs", style=discord.ButtonStyle.primary, custom_id="generate_urls_button")
    async def generate_urls_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        # Check if the user is on cooldown
        if user_id in cooldowns and cooldowns[user_id] > current_time:
            remaining_time = cooldowns[user_id] - current_time
            await interaction.response.send_message(
                f"กรุณารอ {int(remaining_time // 60)} นาทีเพื่อใช้งานอีกครั้ง", ephemeral=True
            )
            return

        # Generate URLs and send the result
        generated_links = generate_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"

        await interaction.response.send_message(result, ephemeral=True)

        # Set the cooldown for the user (2 hours = 7200 seconds)
        cooldowns[user_id] = current_time + 7200

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready')

    # Add the persistent view when the bot starts up
    bot.add_view(MyPersistentView())
    print("Persistent view added")

# Command to generate and send the embed with a button
@bot.command()
async def generate_embed(ctx):
    # Delete the user's command message
    await ctx.message.delete()

    embed = discord.Embed(
        title="สร้างลิงค์แชร์ Facebook",
        description="AONA TOWN",
        color=0x00ff00
    )

    # Send the message with the persistent button
    await ctx.send(embed=embed, view=MyPersistentView())

# Start the bot
server_on()
bot.run(os.getenv('TOKEN'))  # Use environment variable for token
