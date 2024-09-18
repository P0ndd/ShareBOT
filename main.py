import os
import random
import discord
import asyncio
from discord.ext import commands
from discord.ui import Button, View
from server import server_on

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

def generate_random_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

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

# Store the previous message to delete when a new command is called
previous_message = None

@bot.event
async def on_ready():
    print(f'{bot.user} is ready')

@bot.command()
async def generate_embed(ctx):
    global previous_message

    # Delete the user's command message
    await ctx.message.delete()

    # Delete the previous message if it exists
    if previous_message:
        try:
            await previous_message.delete()
        except discord.NotFound:
            pass  # Message was already deleted

    embed = discord.Embed(
        title="สร้างลิงค์แชร์ Facebook",
        description="AONA TOWN",
        color=0x00ff00
    )

    button = Button(label="Generate URLs", style=discord.ButtonStyle.primary)
    view = View()

    async def button_callback(interaction):
        user_id = interaction.user.id
        current_time = discord.utils.utcnow().timestamp()

        # Check if the user is still on cooldown
        if user_id in cooldowns and cooldowns[user_id] > current_time:
            remaining_time = cooldowns[user_id] - current_time
            await interaction.response.send_message(
                f"กรุณารอ {int(remaining_time // 60)} นาทีเพื่อใช้งานอีกครั้ง", ephemeral=True
            )
            return

        # Generate URLs and send the result
        generated_links = generate_urls()
        result = "```\n" + "\n".join(generated_links) + "\n```"

        # Send ephemeral message
        await interaction.response.send_message(result, ephemeral=True)

        # Set the cooldown for the user (2 hours = 7200 seconds)
        cooldowns[user_id] = current_time + 7200

    button.callback = button_callback
    view.add_item(button)

    # Send the new message and store its reference to delete it later
    previous_message = await ctx.send(embed=embed, view=view)

server_on()

bot.run(os.getenv('TOKEN'))
