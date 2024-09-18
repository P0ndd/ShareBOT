import os
import random
import discord
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


@bot.event
async def on_ready():
    print(f'{bot.user} is ready')


@bot.command()
async def generate_embed(ctx):

    embed = discord.Embed(title="สร้างลิงค์แชร์ Facebook ",
                          description="AONA TOWN",
                          color=0x00ff00)

    button = Button(label="Generate URLs", style=discord.ButtonStyle.primary)
    view = View()

    async def button_callback(interaction):
        generated_links = generate_urls()
        result = "\n".join(generated_links)
        await interaction.response.send_message(
            result, ephemeral=True)  # ส่ง URL ให้ผู้ใช้แบบส่วนตัว

    button.callback = button_callback
    view.add_item(button)

    await ctx.send(embed=embed, view=view)


server_on()

bot.run(os.getenv('TOKEN'))
