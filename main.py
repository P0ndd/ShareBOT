import os
import random
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from server import server_on
from datetime import datetime, timedelta
import pytz 

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

# Set Thailand timezone
THAILAND_TZ = pytz.timezone('Asia/Bangkok')

# Function to generate a random number for the links
def generate_random_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

# Function to generate URLs with random numbers attached
def generate_aonatown_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/",
        "https://www.facebook.com/groups/289008456634964/",
        "https://www.facebook.com/groups/fivemthailandcommunity/",
    ]

    generated_links = []
    for i, link in enumerate(links):
        random_number = generate_random_number()
        full_link = link + random_number
        generated_links.append(full_link)
    return generated_links

def generate_sevencity_urls():
    links = [
        "https://www.facebook.com/groups/FiveMThailand/posts/",
        "https://www.facebook.com/groups/289008456634964/posts/",
        "https://www.facebook.com/groups/255834148328219/posts/",
        "https://www.facebook.com/groups/fivemthailandcommunity/posts/",
        "https://www.facebook.com/groups/686633655307229/posts/"
    ]

    generated_links = []
    for i, link in enumerate(links):
        random_number = generate_random_number()
        full_link = f"{link}{random_number}/"
        generated_links.append(full_link)
    return generated_links

# Dictionary to track button press cooldowns for each user
cooldowns = {}

# Task to check and notify users when cooldown expires
@tasks.loop(minutes=1)
async def check_cooldown():
    current_time = discord.utils.utcnow().timestamp()
    for user_id, cooldowns_data in list(cooldowns.items()):
        aonatown_cooldown, sevencity_cooldown = cooldowns_data
        if aonatown_cooldown <= current_time and aonatown_cooldown != 0:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    await user.send(f"คูลดาวน์ของปุ่ม AONATOWN ของคุณหมดแล้ว! คุณสามารถกดปุ่มนี้ได้อีกครั้ง")
                except discord.Forbidden:
                    print(f"Unable to send private message to {user.name}")
            cooldowns[user_id][0] = 0  # Reset AONATOWN cooldown

        if sevencity_cooldown <= current_time and sevencity_cooldown != 0:
            user = await bot.fetch_user(user_id)
            if user:
                try:
                    await user.send(f"คูลดาวน์ของปุ่ม SEVEN CITY ของคุณหมดแล้ว! คุณสามารถกดปุ่มนี้ได้อีกครั้ง")
                except discord.Forbidden:
                    print(f"Unable to send private message to {user.name}")
            cooldowns[user_id][1] = 0  # Reset SEVEN CITY cooldown

# Persistent View class with buttons and custom_id for persistence
class MyPersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view, never times out

    @discord.ui.button(label="AONA TOWN", style=discord.ButtonStyle.primary, custom_id="aonatown_button")
    async def aonatown_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        # Check if the user is on cooldown for AONATOWN
        if user_id in cooldowns and cooldowns[user_id][0] > current_time:
            remaining_time = cooldowns[user_id][0] - current_time
            finish_time = datetime.utcnow() + timedelta(seconds=remaining_time)
            finish_time_local = finish_time.replace(tzinfo=pytz.utc).astimezone(THAILAND_TZ)
            formatted_time = finish_time_local.strftime("%I:%M:%S %p")

            await interaction.response.send_message(
                f"Please wait another {int(remaining_time // 60)} minutes. Your AONATOWN cooldown will expire at {formatted_time} (Thailand time)", ephemeral=True
            )
            return

        # Generate URLs and send the result
        generated_links = generate_aonatown_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"

        await interaction.response.send_message(result, ephemeral=True)

        # Set the cooldown for the user (2 hours = 7200 seconds)
        if user_id not in cooldowns:
            cooldowns[user_id] = [0, 0]  # Initialize with 0 for both AONATOWN and SEVEN CITY
        cooldowns[user_id][0] = current_time + 7200

    @discord.ui.button(label="SEVEN CITY", style=discord.ButtonStyle.primary, custom_id="sevencity_button")
    async def sevencity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        # Check if the user is on cooldown for SEVEN CITY
        if user_id in cooldowns and cooldowns[user_id][1] > current_time:
            remaining_time = cooldowns[user_id][1] - current_time
            finish_time = datetime.utcnow() + timedelta(seconds=remaining_time)
            finish_time_local = finish_time.replace(tzinfo=pytz.utc).astimezone(THAILAND_TZ)
            formatted_time = finish_time_local.strftime("%I:%M:%S %p")

            await interaction.response.send_message(
                f"Please wait another {int(remaining_time // 60)} minutes. Your SEVEN CITY cooldown will expire at {formatted_time} (Thailand time)", ephemeral=True
            )
            return

        # Generate URLs and send the result
        generated_links = generate_sevencity_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"
        
        await interaction.response.send_message(result, ephemeral=True)

        # Set the cooldown for the user (1 hour = 3600 seconds)
        if user_id not in cooldowns:
            cooldowns[user_id] = [0, 0]  # Initialize with 0 for both AONATOWN and SEVEN CITY
        cooldowns[user_id][1] = current_time + 3600

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is ready')

    # Add the persistent view when the bot starts up
    bot.add_view(MyPersistentView())
    print("Persistent view added")

    # Start the cooldown checking task
    check_cooldown.start()

# Command to generate and send the embed with buttons
@bot.command()
async def generate_embed(ctx):
    # Delete the user's command message
    await ctx.message.delete()

    embed = discord.Embed(
        title="สร้างลิงค์แชร์ Facebook",
        color=0x00ff00
    )

    # Send the message with the persistent buttons
    await ctx.send(embed=embed, view=MyPersistentView())

# Start the bot
server_on()
bot.run(os.getenv('TOKEN'))  # Use environment variable for token
