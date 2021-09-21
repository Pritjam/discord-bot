# bot.py
import os
import discord
import youtube_dl
import asyncio


from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

client = commands.Bot(command_prefix="!")
songQueue = []
songCount = 0
nameQueue = []
isActive = False

@client.command(name="remove", help="Removes the given song index from the list.")
async def rm(ctx, index : int):
    global songQueue, nameQueue, songCount
    if index > len(songQueue) or index < 2:
        await ctx.send("That's out of the list! Use skip to remove the current song.")
        return
    if index == 1:
        next()
        return
    songName = songQueue.pop(index - 1)
    nameQueue.pop(index - 1)
    os.remove(songName)

@client.command(name="list", help="Shows the current queue of songs.")
async def ls(ctx):
    global nameQueue
    if(len(nameQueue) == 0):
        await ctx.send("No songs to play!")
        return
    result = ""
    for x in range(len(songQueue)):
        result += str(x + 1) + ". " + nameQueue[x] + "\n"
    await ctx.send(result)

@client.command(name="queue", help="Add a song to the end of the queue")
async def queue(ctx, url : str, pos : int=-1):
    # can"t handle playlists safely yet
    if url.find("playlist") != -1:
        return
    global songQueue
    index = len(songQueue) if pos == -1 else pos
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if (not file.startswith("_")) and file.endswith(".mp3"):
            global songCount, nameQueue
            nameQueue.insert(index, (str(file).rpartition("-")[0] + " Queued by: " + str(ctx.author.nick if ctx.author.nick != None else ctx.author.name)))
            os.rename(file, "_song" + str(songCount) + ".mp3")
            songQueue.insert(index, str("_song" + str(songCount) + ".mp3"))
            songCount += 1
            


@client.command(name="start", help="Starts playing the queue")
async def start(ctx):
    global songQueue, isActive
    if isActive:
        await ctx.send("Already started!")
        return
    nextSong = songQueue[0]
    song_there = os.path.isfile(nextSong)

    voiceChannel = voiceChannel = ctx.author.voice.channel
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    while len(songQueue) > 0:
        # print("going to play")
        
        if not isActive:
            voice.play(discord.FFmpegPCMAudio(songQueue[0]), after=next)
            isActive = True
        await asyncio.sleep(5)
        # print("song played")
    await leave(ctx)

@client.command(name="skip", help="Skips currently playing song")
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


def next(err):
    global songQueue, isActive
    if(len(songQueue) == 0):
        return
    # print(err)
    oldSong = songQueue.pop(0)
    os.remove(oldSong)
    isActive = len(songQueue) == 0

@client.command(name="leave", help="Disconnects the voice bot.")
async def leave(ctx):
    global songCount, isActive
    songCount = 0
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
    for song in songQueue:
        os.remove(song)
    songQueue.clear()
    nameQueue.clear()
    isActive = False


@client.command(name="pause", help="Pauses currently playing song.")
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command(name="resume", help="Resumes current song.")
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


client.run(TOKEN)