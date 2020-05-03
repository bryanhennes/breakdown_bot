import discord
from discord.ext import commands
from discord.utils import get
import os
from pathlib import Path
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix= '.')
#bot_token = 'NzA1NTA4MTEwNzQzMjQwODI1.Xq77bA.vYVFAEJp37ybGn3eKQPZZW7qGH8'

#iterate through all files in songs folder and add each file name to songs list
files = Path('Songs/')
songs = []
#use this list to store the song that last played, that way if someone uses .repeat, the bot will play last song in that list
last_played = []
for file in files.iterdir():
    songs.append(file.name)

#function to format search term entered by user
def transform(str):
    new_str = ''
    for word in str.split(" "):
        if len(word) > 1:
            new_str += word[0].upper() + word[1:len(word)] + " "
        else:
            new_str += word[0].upper() + " "
    return new_str

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='hey')
async def hey(ctx):
    response = ('hey, wanna hear a breakdown?')
    await ctx.send(response)
    
@bot.command(pass_context=True)
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await voice.disconnect()
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The {bot.user} has connected to {channel}")
    await ctx.send(f"{bot.user} is here to open up the pit.")

@bot.command(pass_context=True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The {bot.user} has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print(f"{bot.user} was told to leave the channel, but he was not in one.")
        await ctx.send(f"Don't think I was in that channel.")


@bot.command(pass_context=True)
async def play(ctx):
    #when .play is used, use rand num generator to pick a song from songs list, check each time to see if already in last_played list, if so keep picking until new song is chosen to avoid repeats.
    #when a new song is chosen, play that song, and add that song to last_played list
    current_song = songs[random.randint(0, len(songs)-1)]
    if len(last_played) == 0:
        last_played.append(current_song)
    while current_song in last_played:
        current_song = songs[random.randint(0, len(songs)-1)]
    last_played.append(current_song)
   
    voice.play(discord.FFmpegPCMAudio(f'{current_song}'), after=lambda e: print(f"{current_song} has finished playing."))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 1.0

    await ctx.send(f'Now playing: {current_song[:-4]}')

@bot.command(pass_context=True)
async def repeat(ctx):
    #repeat function will play the last song added to last_played list
    current_song = last_played[-1]
    voice.play(discord.FFmpegPCMAudio(f'{current_song}'), after=lambda e: print(f"{current_song} has finished playing."))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 1.0

    await ctx.send(f'Now playing: {current_song[:-4]}')



@bot.command(pass_context=True)
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Breakdown paused")
    else:
        print("Nothing is currently playing")
        await ctx.send("Can't pause when nothing is playing")

@bot.command(pass_context=True)
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Breakdown resumed")
    else:
        print("Nothing was paused")
        await ctx.send("Can't resume something that wasn't already playing")

@bot.command(pass_context=True)
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Breakdown stopped")
    else:
        print("Nothing is currently playing")
        await ctx.send("Can't stop something that is not playing")

@bot.command(pass_context=True)
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music skipped")
        voice.stop()
        await ctx.send("Breakdown skipped")
        current_song = songs[random.randint(0, len(songs)-1)]
        while current_song in last_played:
            current_song = songs[random.randint(0, len(songs)-1)]
        last_played.append(current_song)
   
        voice.play(discord.FFmpegPCMAudio(f'{current_song}'), after=lambda e: print(f"{current_song} has finished playing."))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 1.0

        await ctx.send(f'Now playing: {current_song[:-4]}')

@bot.command(pass_context=True)
async def find(ctx, file_name):
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_playing():
        await ctx.send("Wait until this breakdown is over, bruv.")
    for song in songs:
        if transform(file_name) in song:
            voice.play(discord.FFmpegPCMAudio(f'{song}'), after=lambda e: print(f"{song} has finished playing."))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 1.0

            await ctx.send(f'Now playing: {song[:-4]}')
            last_played.append(song)
   
#this function will return in chat all of the songs that have search term in file name
@bot.command(pass_context=True)
async def check(ctx, search):
    for song in songs:
        if transform(search) in song:
            await ctx.send(f'{song}')
    


bot.run(TOKEN)



