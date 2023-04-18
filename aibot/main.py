import discord
from discord.ext import commands
from playwright.async_api import async_playwright
from datetime import datetime
import re

intents = discord.Intents.all()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def chat(ctx, character_id):
    async with async_playwright() as playwright:
        print (character_id)
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f'https://beta.character.ai/chat?char={character_id}')
        await page.get_by_role("button", name="Accept").click()
        await ctx.send("Enter your first prompt to start the conversation.")

        while True:
            message = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            await send_message(page, message.content)
            chara = await page.query_selector('div.chattitle.p-0.pe-1.m-0')
            chara_name = (await chara.inner_text()).strip() 
            typing_message = await ctx.send(f"{chara_name} is typing...")
            await page.wait_for_selector('.swiper-button-next')
            await (await page.wait_for_selector('.swiper-button-next')).click()
            div = await page.query_selector('div.msg.char-msg')
            output_text = (await div.inner_text()).strip()
            stripped_output_text = re.sub(r'\s+', ' ', output_text).strip()
            now = datetime.now()
            time_str = f"[{now:%H:%M}]"
            await ctx.send(f"{stripped_output_text}")

            if message.author.bot:
                break
            if message.content == "!stop":
                await ctx.send("Interaction has been ended.")
                break

        await context.close()
        await browser.close()
        await typing_message.delete()

async def send_message(page, message):
    await page.get_by_placeholder("Type a message").fill(message)
    await page.get_by_placeholder("Type a message").press("Enter")
    await page.wait_for_selector('div.msg.char-msg')  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

bot.run("TOKEN HERE")
