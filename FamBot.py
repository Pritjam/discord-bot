# bot.py
import os
import discord
import youtube_dl
import asyncio


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
    if(len(nameQueue) == 0):
        await ctx.send("No songs to play!")
        return
    result = ""
    for item in nameQueue:
        result += "- " + item + "\n"
    await ctx.send(result)

@client.command(name='queue')
async def queue(ctx, url : str):
    # print("AAA")
    if url.find("playlist") != -1:
        return
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
        if not (voice.is_playing() or voice.is_paused()):
            voice.play(discord.FFmpegPCMAudio(songQueue[0]), after=next)
        await asyncio.sleep(5)
        # print("song played")
    await leave(ctx)

@client.command(name='skip')
async def skip(ctx):
    await stop(ctx)


def next(err):
    global songQueue
    if(len(songQueue) == 0):
        return
    # print(err)
    oldSong = songQueue.pop(0)
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
    for song in songQueue:
        os.remove(song)
    songQueue.clear()
    nameQueue.clear()


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
    global songQueue, nameQueue
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


client.run(TOKEN)