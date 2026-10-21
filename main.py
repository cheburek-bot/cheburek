import io
import os
import random
import re
from pathlib import Path

import discord
from cheburek_core import Chain, MemeGenerator
from dotenv import load_dotenv

load_dotenv()

chain = Chain()
meme_gen = MemeGenerator()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"🥟 Logged in as {bot.user}!")


@bot.event
async def on_message(ctx: discord.Message):
    if ctx.author.bot or not ctx.guild:
        return

    guild_id = str(ctx.guild.id)

    # Clean up and process the words

    clean_content = re.sub(
        r"https?:\/\/[^\s)\]]+",
        "",
        ctx.content,
    )
    clean_content = re.sub(r"<@!?\d+>", "", clean_content)
    clean_content = re.sub(r"\s+", " ", clean_content).strip()

    words = clean_content.split(" ")
    chain.process_words(words, guild_id)

    # Reply when someone mentioned/replied to bot

    mentioned = bot.user in ctx.mentions

    replied = (
        ctx.reference is not None
        and isinstance(ctx.reference.resolved, discord.Message)
        and ctx.reference.resolved.author == bot.user
    )

    if mentioned or replied:
        try:
            message = chain.generate_message(random.randint(2, 12), guild_id)
            await ctx.reply(message)
        except Exception as e:
            print("Failed to reply a message:", e)
    else:
        # Try a chance to generate and send a message

        if random.random() < float(os.environ["MESSAGE_CHANCE"]):
            try:
                message = chain.generate_message(random.randint(2, 12), guild_id)
                await ctx.channel.send(message)
            except Exception as e:
                print("Failed to send message:", e)


@bot.command(
    description="Generate a message",
    description_localizations={"ru": "Сгенерировать сообщение"},
)
async def generate(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    guild_id = str(interaction.guild_id)

    if chain.get_words_count(guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    message = chain.generate_message(random.randint(2, 12), guild_id)

    await interaction.response.send_message(message)


@bot.command(
    description="Generate a Jacque Fresco meme",
    description_localizations={"ru": "Сгенерировать мем Жак Фреско"},
)
async def fresco(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    guild_id = str(interaction.guild_id)

    await interaction.response.defer()

    if chain.get_words_count(guild_id) == 0:
        embed = discord.Embed(
            title="Ошибка",
            description="Не хватает слов! Отправьте больше сообщений и повторите команду.",
            color=discord.Color.red(),
        )
        await interaction.respond(embed=embed)
        return

    message = chain.generate_message(random.randint(2, 8), guild_id)
    img = meme_gen.create_fresco(message)

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)

        await interaction.respond(
            file=discord.File(fp=image_binary, filename="fresco.png")
        )


@bot.command(
    description="Display bot stats",
    description_localizations={"ru": "Показать статистику"},
)
async def stats(interaction: discord.Interaction):
    if not interaction.guild_id:
        return

    guild_id = str(interaction.guild_id)

    words = chain.get_words_count(guild_id)
    links = chain.get_links_count(guild_id)

    if interaction.guild:
        name = interaction.guild.name
    else:
        name = interaction.guild_id

    embed = discord.Embed(
        title=f"Статистика ({name})",
        description="Количество изученных данных",
        color=discord.Color.orange(),
    )

    embed.add_field(name="📖 Слова", value=f"{words} слов")
    embed.add_field(name="🔗 Связи", value=f"{links} связей")

    await interaction.response.send_message(embed=embed)


bot.run(os.environ["TOKEN"])
