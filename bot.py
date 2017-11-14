#!/usr/bin/python3.6
import discord
import json
import os
import sys
import time
import asyncio

bot = discord.Client()
config = json.load(open(os.getcwd() + "/config/config.json"))
cmds = json.load(open(os.getcwd() + "/config/cmd.json"))
token = config["general"]["token"]
mlogging = config["logging"]["messages"]
clogging = config["logging"]["commands"]
commands = []

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    print("Servers:")
    for server in bot.servers:
        print("  " + server.name)
    print("----------------")
    print("")

    print("Updating User List...")
    await bot.change_presence(game=discord.Game(name="Updating Users..."))
    await updateUsers()
    print("User List Updated!")
    
    await bot.change_presence(game=discord.Game(name="*help"))
    if bot.user.name != "Starlow":
        await bot.edit_profile(username="Starlow")

    # Add commands to command list
    for command in dir(cmd):
            if not command.startswith("_"):
                commands.append(command)

@bot.event
async def on_message(message):

    await updateUsers() #Quickly update the users

    if mlogging == True:
        print(message.server.name + " | #" + message.channel.name + " | " + message.author.name + ": " + message.content)
        # log.write(message.author.name + ": " + message.content)
        # log.write("\r")
        # log.flush()
    
    if message.content.startswith("*"):
        if message.author.bot == True:
            print(message.server.name + " | #" + message.channel.name + " | " + message.author.name + " tried to use " + message.content + " but is not permitted to do so!")
            # log.write(message.author.name + "tried to use " + message.content + " but is not permitted to do so!")
            # log.write("\r")
            # log.flush()
            return
        
        if clogging == True:
            print(message.server.name + " | #" + message.channel.name + " | " + message.author.name + ": " + message.content)
            # log.write(message.author.name + ": " + message.content)
            # log.write("\r")
            # log.flush()

        command = message.content.split()[0][1:]
        args = message.content.split()
        args.remove(args[0])
        # print(str(args))
        for c in commands:
            if c == command:
                if await isBlacklisted(message.server, message.author, c):
                    await getattr(cmd, command)(args, message)

# await def parseCommand(file):
#     lines = file.readlines()

#     for line in lines:
#         cmd = line.split()[0]
#         args = line.split()[1:]

#         if cmd == "say":
#             for a in args:
#                 argstr += a + " "
#             await bot.send_message(message.channel, argstr)

async def updateUsers():
    for server in bot.servers:
        server_dir = os.getcwd() + "/config/users/" + server.id + "/"
        if os.path.isdir(server_dir):
            None
        else:
            os.mkdir(server_dir)
            os.mkdir(server_dir + server.name.replace("/", "-"))
        for user in server.members:
            if user.bot: # We don't need to store anything for bots
                continue
            user_dir = os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/"
            # User dir
            if os.path.isdir(user_dir):
                continue
            else:
                print("Creating user data for user " + user.name + " on server " + server.name)
                os.mkdir(user_dir)
                os.mkdir(user_dir + user.name.replace("/", "-"))
            # User perms
            if os.path.exists(user_dir + "perms"):
                print(user.name + "'s perms file already exists")
            else:
                if user.id == "194822900577075200":
                    file = open(user_dir + "perms", "w")
                    file.write("Bot Owner")
                    file.close()
                else:
                    file = open(user_dir + "perms", "w")
                    file.write("Everyone")
                    file.close()
            # User bl commands
            if os.path.exists(user_dir + "blacklisted_commands"):
                print(user.name + "'s blacklisted commands file already exists")
            else:
                file = open(user_dir + "blacklisted_commands", "w")
                file.close()
            # User bank
            if os.path.exists(user_dir + "bank"):
                print(user.name + "'s bank file already exists")
            else:
                file = open(user_dir + "bank", "w")
                file.write("None\n")
                file.write("None")
                file.close()
    return

async def getPerm(server, user):
    if os.path.isdir(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/") == False:
        print("Error: " + user.name + " doesn't have existing user info!")
        return "User Does Not Exist!"
    try:
        file = open(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/perms")
        perm = file.readline().replace("\n", "")
        file.close()
        return str(perm)
    except:
        return "User Does Not Exist!"

async def setPerm(server, user, perm):
    if os.path.isdir(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/") == False:
        print("Error: " + user.name + " doesn't have existing user info!")
        return "User Does Not Exist!"
    try:
        file = open(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/perms", "w")
        file.write(perm)
        file.close()
        return(user.name + " is now " + perm + "!")
    except:
        return "User Permission File Does Not Exist!"

async def parsePerm(perm):
    perms = {"Bot Owner": 99999,
             "Super Owner" : 3,
             "Owner" : 2,
             "Admin" : 1,
             "Everyone" : 0}
    try:
        return perms[perm]
    except:
        return 0

async def parseUser(server, toParse):
    if toParse == None or server == None:
        print("Function parseUser() didn't get any arguments or didn't get a server!")
        return
    for user in server.members:
        if toParse == user.id or toParse == user.name or toParse == user.nick or toParse == "<@!" + user.id + ">" or toParse == "<@" + user.id + ">":
            return user
    print(toParse + " not found...")
    return

async def hasPerms(server, user, minPerms):
    if await parsePerm(await getPerm(server, user)) >= await parsePerm(minPerms):
        return True
    return False

async def blacklistCommand(server, user, command):
    print(":P")
    if os.path.isdir(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/") == False:
        print("Error: " + user.name + " doesn't have existing user info!")
        return
    try:
        file = open(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/blacklisted_commands", "r+")
        file.write(command + "\n")
        file.close()
        print("Blacklisted " + command + " for user " + user.name + " on " + server.name)
    except:
        print("Failed to blacklist command " + command + " for user " + user.name + " on server " + server.name)
        return
    await bot.send_message(user, "You are no longer allowed to use *" + command + " on " + server.name + "!")

async def isBlacklisted(server, user, command):
    if os.path.isdir(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/") == False:
        print("Error: " + user.name + " doesn't have existing user info!")
        return
    try:
        file = open(os.getcwd() + "/config/users/" + server.id + "/" + user.id + "/blacklisted_commands", "r")
        for line in file.readlines:
            if line.replace("\n", "") == command or line.replace("\n", "") == "*":
                return True
        return False
    except:
        return True

class cmd:
    async def help(args, message):
        cemb = discord.Embed(color=discord.Color.green())
        addedcategories = []
        categories = {}
        for c in commands:
            usage = cmds[c]["usage"]
            description = cmds[c]["description"]
            perm = cmds[c]["perms"]
            category = cmds[c]["category"]

            
            
            # try:
            #     cemb.add_field(name=c, value="Usage: " + str(usage) + "\nDescription: " + description + "\nCategory: " + category)
            # except:
            #     print("Error in " + c)
            #     continue
        await bot.send_message(destination=message.channel, embed=cemb)

    async def say(args, message):
        if not await hasPerms(message.server, message.author, "Admin"):
            return
        await bot.delete_message(message)
        argstr = ""
        for a in args:
            argstr += a + " "
        await bot.send_message(message.channel, argstr)

    async def invite(args, message):
        await bot.send_message(message.author, "https://discordapp.com/oauth2/authorize?client_id=369599186284445707&scope=bot&permissions=738454767")
        await bot.send_message(message.channel, "<@" + message.author.id + ">, I DM'ed you my invite link. Hope to see you on your server!")

    async def preventsuicide(args, message):
        await bot.send_message(message.channel, "<@" + message.author.id + ">, 1-800-273-8255")

    async def userinfo(args, message):
        name = " ".join(args)
        if len(args) == 0:
            user = message.author
        else:
            print(args[0])
            if args[0] == "@everyone" or args[0].startswith("@") or args[0].startswith():
                await bot.delete_message(message)
                await blacklistCommand(message.author, message.server, "userInfo")
                return
            user = await parseUser(message.server, name)
        emb = discord.Embed(color = discord.Color.green())
        d = message.channel

        if user == None:
            await bot.send_message(message.channel, name + " was not found! Try mentioning them or using their User ID.")
            return

        nick = user.nick
        
        if nick == None:
            nick = "No Nickname"
        # emb.set_image(user.avatar_url)
        # emb.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
        emb.set_thumbnail(url=user.avatar_url)
        emb.add_field(name="Name", value=user.name)
        emb.add_field(name="Nickname", value=nick)
        emb.add_field(name="User ID", value=user.id)
        emb.add_field(name="Current Balance", value="Coming Soon!")
        emb.set_footer(text="Permission: " + await getPerm(message.server, user))

        await bot.send_message(destination=message.channel, embed=emb)

        #await bot.send_message(message.channel, "`Name: " + user.name + "\nNickname: " + nick + "\nUser ID: " + user.id + "`")
    
    async def owner(args, message):
        if await getPerm(message.server, message.author) != "Super Owner":
            return
        name = " ".join(args)
        user = await parseUser(message.server, name)
        if user == None:
            await bot.send_message(message.channel, args[0] + " was not found!")
            return
        reply = await setPerm(message.server, user, "Owner")
        await bot.send_message(message.channel, reply)

    async def admin(args, message):
        if not await hasPerms(message.server, message.author, "Owner"):
            return
        name = " ".join(args)
        user = await parseUser(message.server, name)
        if user == None:
            await bot.send_message(message.channel, args[0] + " was not found!")
            return
        if user.name == "bennyman123abc":
            await bot.send_message(message.channel, "What the fuck are you doing peasant? Ben's the super overlord owner of all overlordiness!")
            return
        reply = await setPerm(message.server, user, "Admin")
        await bot.send_message(message.channel, reply)

    async def suckit(args, message):
        if not await parsePerm(await getPerm(message.server, message.author)) >= await parsePerm(cmds["suckit"]["perms"]):
            return
        await bot.delete_message(message)
        name = " ".join(args)
        user = await parseUser(message.server, name)
        if user == None:
            await bot.send_message(message.channel, args[0] + " was not found!")
            return
        nick = user.nick
        if user.nick == None:
            await bot.send_message(message.channel, "8=====D <-- " + user.name + "'s lunch!")
        else:
            await bot.send_message(message.channel, "8=====D <-- " + user.nick + "'s lunch!")

    async def updateusers(args, message):
        if await hasPerms(message.server, message.author, "Admin") == False:
            return
        await updateUsers()
        await bot.send_message(message.channel, "User list updated!")

    async def giveperm(args, message):
        if not await hasPerms(message.server, message.author, "Super Owner"):
            return
        user = await parseUser(message.server, args[0])
        if user == None:
            await bot.send_message(message.channel, args[0] + " was not found!")
            return
        args.remove(args[0])
        if " ".join(args) == "Bot Owner":
            await bot.send_message(message.channel, "You are not allowed to give someone that permission!")
        reply = await setPerm(message.server, user, " ".join(args))
        await bot.send_message(message.channel, reply)

bot.run(token)
        
