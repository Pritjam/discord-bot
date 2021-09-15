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
nameQueue = []

@client.command(name='list')
async def ls(ctx):
    global nameQueue
    result = ""
    for item in nameQueue:
        result += "- " + item + "\n"
    await ctx.send(result)

@client.command(name='queue')
async def queue(ctx, url : str):
    # print("AAA")
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
        if (not file.startswith("_")) and file.endswith(".mp3"):
            global nowPlaying, nameQueue
            nameQueue.append(str(file).rpartition('-')[0])
            os.rename(file, "_song" + str(nowPlaying) + ".mp3")
            songQueue.append(str("_song" + str(nowPlaying) + ".mp3"))
            nowPlaying += 1


@client.command(name='play')
async def play(ctx, url : str="null"):
    global songQueue
    if not url == "null":
        await queue(ctx, url)
    nextSong = songQueue[0]

    song_there = os.path.isfile(nextSong)

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    while(len(songQueue) > 0):
        # print("going to play")
        voice.play(discord.FFmpegPCMAudio(songQueue[0]), after=next)
        while(voice.is_playing()):
            pass
        # print("song played")
    await leave(ctx)

# @client.command(name='skip')
# async def skip(ctx):
#     nowPlaying = 9

def next(err):
    global songQueue
    if(len(songQueue) == 0):
        return
    # print(err)
    oldSong = songQueue.pop()
    os.remove(oldSong)

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