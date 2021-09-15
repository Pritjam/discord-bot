# bot.py
import os
import random
import discord
from discord.ext.commands.core import is_nsfw
import youtube_dl


from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = commands.Bot(command_prefix='!')
songQueue = []
nowPlaying = 0
songQueue

@client.command(name='queue')
async def queue(ctx, url : str):
    global songQueue
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if not file.startswith("_"):
            global nowPlaying
            os.rename(file, "_song" + nowPlaying + ".mp3")
            songQueue.append(str("_song" + nowPlaying + ".mp3"))
            nowPlaying += 1


@client.command(name='play')
async def play(ctx, url : str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("song.mp3"))

@client.command(name='skip')
async def skip(ctx):
    nowPlaying = 9

async def next(ctx):
    global songQueue

    if(len(songQueue) == 0):
        leave(ctx)
        return
    oldSong = songQueue.pop()
    nextSong = songQueue[0]
    song_there = os.path.isfile(nextSong)
    if not song_there:
        print("Error! No song to play now!")
        return
    
    


@client.command()
async def leave(ctx):
    global nowPlaying
    nowPlaying = 0
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

client.run(TOKEN)