import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio
import yt_dlp

# Создаем клиент Discord
intents = discord.Intents.default().all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Функция для проверки, что бот подключен к голосовому каналу
async def ensure_voice(ctx):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send('Вы должны быть подключены к голосовому каналу.')

# Команда для воспроизведения музыки
@bot.command()
async def play(ctx, *, query):
    await ensure_voice(ctx)
    vc = ctx.voice_client

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f'ytsearch:{query}', download=False)
        url2 = info['entries'][0]['url']
        source = FFmpegPCMAudio(url2, executable="ffmpeg")
        vc.play(source)

        # Отправляем название воспроизводимой песни
        await ctx.send(f"Сейчас играет: **{info['title']}**")

# Обработчик реакций на сообщения
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    ctx = await bot.get_context(reaction.message)
    if reaction.emoji == '⏸️':  # Если нажата реакция для паузы
        await pause(ctx)
    elif reaction.emoji == '▶️':  # Если нажата реакция для возобновления
        await resume(ctx)
    elif reaction.emoji == '⏹️':  # Если нажата реакция для остановки
        await stop(ctx)

# Команда для паузы воспроизведения
async def pause(ctx):
    await ensure_voice(ctx)
    vc = ctx.voice_client
    if vc.is_playing():
        vc.pause()
        await ctx.message.add_reaction('⏸️')  # Добавляем эмодзи для паузы
        await ctx.send("Воспроизведение приостановлено.")

# Команда для возобновления воспроизведения
async def resume(ctx):
    await ensure_voice(ctx)
    vc = ctx.voice_client
    if vc.is_paused():
        vc.resume()
        await ctx.message.add_reaction('▶️')  # Добавляем эмодзи для возобновления
        await ctx.send("Воспроизведение возобновлено.")

# Команда для остановки воспроизведения
async def stop(ctx):
    await ensure_voice(ctx)
    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()
        await vc.disconnect()
        await ctx.message.add_reaction('⏹️')  # Добавляем эмодзи для остановки
        await ctx.send("Воспроизведение остановлено и бот отключен от голосового канала.")

# Запускаем бота
bot.run('MTE5Mjk4MzY1MDk4NDI3MTg4Mg.GyJmIg.TVVZ6EcAwg5HRwX89L0vYi9NCYbpxkOnUeTdjM')