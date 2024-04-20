import discord
from discord.ext import commands
from discord import Interaction
from discord import ui
import requests
import json
import aiohttp
import io
from datetime import datetime
import asyncio
import config


TOKEN = config.TOKEN
WEBHOOK_URL = config.WEBHOOK_URL
COUNTER_FILE = config.COUNTER_FILE

async def send_message_via_webhook(message_content):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
        await webhook.send(message_content)

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Bot-Prefix
bot = commands.Bot(command_prefix='!', intents=intents)

async def update_presence():
    await bot.wait_until_ready()

    while not bot.is_closed():
        # Request Counter
        try:
            with open(COUNTER_FILE, "r") as file:
                request_counter = int(file.read())
        except FileNotFoundError:
            request_counter = 0

        # Set Discord Rich Presence
        activity = discord.Activity(name=f"Total Requests: {request_counter}",
                                    type=discord.ActivityType.playing)
        await bot.change_presence(activity=activity)

        # Wait 5 minutes before updating again
        await asyncio.sleep(5)  # 300 Seconds = 5 Minutes


@bot.event
async def on_ready():
    print(f'Welcome to {bot.user.name}!\nLogged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)        

    # Start the task to update the presence
    bot.loop.create_task(update_presence())

@bot.command(name="wata", description="WATA Certification")
async def wata(ctx, cert_id: str=None):  # Certification ID
    if not cert_id:
        await ctx.send("Certification Number missing!")  # Error Message if Certification ID is missing
        return


    # Update request counter +1
    try:
        with open(COUNTER_FILE, "r+") as file:
            request_counter = int(file.read())
            request_counter += 1
            file.seek(0)
            file.write(str(request_counter))
            file.truncate()
    except FileNotFoundError:
        with open(COUNTER_FILE, "w") as file:
            file.write("1")

    # API Request Site
    url = f'https://api.watagames.com/api/certdetails/{cert_id}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    wataurl = "https://www.watagames.com/cert/details/" + cert_id

    # Request JSON
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            # Check if the request was successful 
            if response.status == 200:
                # Wait for JSON response
                json_data = await response.json()

                # Check if there is an attachment, if not set datum to N/A
                if 'attachments' in json_data and json_data['attachments'] and 'createdAt' in json_data['attachments'][0]:
                    timestamp = json_data['attachments'][0]['createdAt']
                    datetime_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                    datum = datetime_obj.strftime("%d-%m-%Y")
                else:
                    datum = "N/A"

                # Create Embed Message
                embed = discord.Embed(title= json_data['game']['name'] + " | " + json_data['game']['platforms'], 
                                      url = wataurl,
                                      color=0x00d8f5, 
                                      timestamp=datetime.now())

                embed.add_field(name="Certification Number", value=json_data['label'], inline=True)
                embed.add_field(name="Grading Date", value=datum, inline=True)

                embed.add_field(name="", value="", inline=True)

                embed.add_field(name="Title", value=json_data['game']['name'], inline=True)
                embed.add_field(name="Year", value=json_data['game']['year'], inline=True)            

                embed.add_field(name="", value="", inline=True)

                embed.add_field(name="System", value=json_data['game']['platforms'], inline=True)
                embed.add_field(name="Country of Release", value=json_data['region'], inline=True)

                embed.add_field(name="", value="", inline=True)

                embed.add_field(name="Publisher", value=json_data['game']['publisher'], inline=True)
                embed.add_field(name="Overal Grade", value=json_data['grade']['overallGrade'], inline=True)

                embed.add_field(name="", value="", inline=True)

                embed.add_field(name="Box Grade", value=json_data['grade']['box'], inline=True)

                # Check if the seal grade is empty or NULL if so set it to N/A
                if json_data['grade'].get('seal', '') in ["NULL", ""]:
                    seal_value = "N/A"
                else:
                    seal_value = json_data['grade']['seal']

                embed.add_field(name="Seal Grade", value=seal_value, inline=True)

                embed.add_field(name="", value="", inline=True)

                # Check if instruction and cartridge exist and not NULL
                if 'instruction' in json_data['grade'] and json_data['grade']['instruction'] is not None and \
                    'cartridge' in json_data['grade'] and json_data['grade']['cartridge'] is not None:
                    embed.add_field(name="Manual", value=json_data['grade']['instruction'], inline=True)
                    embed.add_field(name="Cart", value=json_data['grade']['cartridge'], inline=True)
                    embed.add_field(name="", value="", inline=True)

                # Check if variants exist and not NULL
                if 'variants' in json_data['grade'] and json_data['grade']['variants'] is not None:
                    # Remove all asterisks (*) from the variants
                    cleaned_variants = ['• ' + variant.replace('*', '') for variant in json_data['grade']['variants']]
                    # Convert the list to a string
                    variants_value = '\n'.join(cleaned_variants)
                    # Add the variants to the embed
                    embed.add_field(name="Variants", value=variants_value, inline=True)

                # Check if notes exist and not NULL
                if 'notes' in json_data['grade'] and json_data['grade']['notes'] is not None:
                    embed.add_field(name="Notes", value=json_data['grade']['notes'], inline=False)
                    embed.add_field(name="", value="", inline=True)


                embed.set_thumbnail(url="https://www.watagames.com/images/logo.png")
                embed.set_footer(text="Made by nichtlegacy | Request Nr. " + str(request_counter), icon_url="http://193.111.248.231/images/legacy.jpg")
                embed.set_author(name="WATA Game Certification", url="https://www.watagames.com/", icon_url="https://www.watagames.com/images/logo.png")


                # Create Button-View
                
                button1 = ui.Button(style=discord.ButtonStyle.blurple,label="WATA", emoji=discord.PartialEmoji.from_str("<:wata_logo:1231261401742577725>"))
                button2 = ui.Button(style=discord.ButtonStyle.green,label="VGA", emoji=discord.PartialEmoji.from_str("<:vga_logo:1231261412601495634>"), disabled=True)
                button3 = ui.Button(style=discord.ButtonStyle.red,label="Pixel", emoji=discord.PartialEmoji.from_str("<:pixel_logo:1231261642252226570>"), disabled=True)
                button4 = ui.Button(style=discord.ButtonStyle.gray,label="CGC", emoji=discord.PartialEmoji.from_str("<:cgc_logo:1231273337150373918>"), disabled=True)
                button5 = ui.Button(style=discord.ButtonStyle.url,label="GitHub", emoji=discord.PartialEmoji.from_str("<:legacylogo:1182883101148455012>"), url="https://github.com/lorenzjan/certification_bot")


                view = discord.ui.View()

                view.add_item(button1)
                view.add_item(button2)
                view.add_item(button3)
                view.add_item(button4)
                view.add_item(button5)

                # Determining the image based on the value of "attachmentTypeId"
                image_index = 0
                if json_data['attachments']:
                    for attachment in json_data['attachments']:
                        if attachment.get('attachmentTypeId') == 15:
                            image_index = json_data['attachments'].index(attachment)
                            break

                # Set the image URL based on the attachmentTypeId
                if len(json_data['attachments']) > image_index:
                    imageurl = "https:" + json_data['attachments'][image_index]['highResUrl']
                else:
                    imageurl = None

                # If no image with attachmentTypeId 15 was found and there is no image with index 0
                if image_index == 0 and not (json_data['attachments'] and json_data['attachments'][0].get('attachmentTypeId') == 15) and imageurl is None:
                    # Search for an image with index 0
                    if json_data['game'].get('imgUrl'):
                        imageurl = json_data['game']['imgUrl']

                if imageurl:
                    # Get the image from the URL
                    async with session.get(imageurl, headers=headers) as img_response:
                        if img_response.status == 200:
                            # Receive the image data
                            image_data = await img_response.read()
                            # Embedding the image as a file object and adding it to the embed.
                            file = discord.File(io.BytesIO(image_data), filename='image.png')
                            embed.set_image(url="attachment://image.png")
                            await ctx.send(embed=embed, file=file, view=view)
                        else:
                            await ctx.send(embed=embed, view=view)
                            
                            # Webhook Error Message
                            message = f"The request for the image was not successful. Status code: {img_response.status}, {json_data['label']}"
                            await send_message_via_webhook(message)
                else:
                    # If there is no image, send the embed without the image
                    await ctx.send(embed=embed, view=view)

                    # Webhook Error Message
                    message = f"No image found. Game: {json_data['label']}"
                    await send_message_via_webhook(message)

            else:
                # Send error message, then wait 5 seconds and delete the message
                message = await ctx.send(f"{ctx.author.mention} Your request was not successful. Error code: {response.status}")
                await asyncio.sleep(5)
                await message.delete()

                # Webhook Error Message
                now = datetime.now()
                message = f"`{now.strftime("%H:%M:%S")}` There was an error in the following game: **`{cert_id}`** by **`{ctx.message.author.name}`**"
                await send_message_via_webhook(message)


@bot.command()
async def request_count(ctx):
    try:
        with open(COUNTER_FILE, "r") as file:
            request_counter = int(file.read())
            await ctx.send(f"Total number of requests: {request_counter}")
    except FileNotFoundError:
        await ctx.send("Total number of requests: 0")


# Start the bot
bot.run(TOKEN)
