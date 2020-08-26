import os
import asyncio
import discord
import operator

from dotenv import load_dotenv
from datetime import date

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

potd = {
		0 : ['n/a', 'n/a', 'n/a'],
		1 : ['Paula the painter had just enough paint for 30 identically sized rooms. Unfortunately, on the way to work, three cans of paint fell off her truck, so she had only enough paint for 25 rooms. How many cans of paint did she use for the 25 rooms?', '15', '2009 AMC 10B'],
	}

bot = commands.Bot(command_prefix='!')
members={}
day = 0

async def daily():
	await bot.wait_until_ready()
	channel = bot.get_channel(747961969843110029)
	guild = discord.utils.get(bot.guilds, name="MathClub")
	global day
	while not bot.is_closed():
		await channel.send("The answer was ||" + potd[day][1] + "||")
		await channel.send("Source: " + potd[day][2])
		await channel.send("New Question! DM me answers in exact numeric form with no spaces, punctuation, or extra words.")
		day+=1
		for member in members:
			score = members[member][0]
			members[member] = [score, 5]
		for member in guild.members: 
			role = discord.utils.get(member.guild.roles, name="POTDSolvers")
			if role in member.roles:
				await member.remove_roles(role)
		await channel.send(potd[day][0])
		await updateLeaderboard()
		await asyncio.sleep(86400)
			

async def updateLeaderboard():
	channel = bot.get_channel(748030327729160243)
	today = str(date.today())
	await channel.send("Scoreboard as of " + today)
	for key, values in sorted(members.items(), key=operator.itemgetter(1), reverse=True):
		if(values[0] > 0):
			await channel.send(key + "\t" +str(values[0]))


@bot.event
async def on_ready():
	print(f'{bot.user.name} is connected to Discord!')
	for guild in bot.guilds:
			for member in guild.members:
				members[member.name] = [0, 5]

@bot.command(name='score')
async def getScore(ctx, member: discord.Member = None):
	if member is None:
		member = ctx.message.author.name
	await ctx.send(members[member][0])

@bot.event
async def on_member_join(member):
	members[{member.name}] = [0, 5]
	await member.create_dm()
	await member.dm_channel.send(
		f'Hey {member.name}, welcome to Math Club! Thanks for joining. We have intro meetings (if its your first time in the club) Tuesdays at 3:15 and Advanced meetings Wednesdays at 3:15. Hope to see you there! Make sure to check out the #welcome section of the discord to find out more.'
	)

@bot.event
async def on_message(message):
	if message.guild is None and message.author != bot.user:
		if message.content == potd[day][1]:
			#add role solved
			await message.author.create_dm()
			points = members[message.author.name][1]
			if(points==0):
				await message.author.dm_channel.send('You already answered this challenge.')
			else:
				await message.author.dm_channel.send(
				f'Correct! You earned {members[message.author.name][1]} points for today.'
				)
			members[message.author.name][0] += members[message.author.name][1]
			members[message.author.name][1] = 0
			member = bot.get_guild(613484457118400555).get_member(message.author.id)
			print(member.name)
			role = discord.utils.get(member.guild.roles, name="POTDSolvers")
			print(role.name)
			await member.add_roles(role)
		else:
			await message.author.create_dm()
			if(members[message.author.name][1]==0):
				await message.author.dm_channel.send('You already answered this challenge.')
			else:
				await message.author.dm_channel.send(
					f'Try again!'
				)
				members[message.author.name][1] = members[message.author.name][1] - 1
				if members[message.author.name][1] < 1:
					members[message.author.name][1] = 1
	await bot.process_commands(message)


bot.loop.create_task(daily())
bot.run(TOKEN)