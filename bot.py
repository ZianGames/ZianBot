#!/usr/bin/python3.6
import discord
import json
import os
import sys
import time
import asyncio
import random
from shutil import copyfile

bot_version = "1.0"
configfile = os.getcwd() + "/config/config.json"
if not os.path.exists(configfile):
    copyfile(os.getcwd() + "/config/config_template.json", configfile)
    print("Config has been generated. Fill out the bot token and run this again.")
    sys.exit()
bot = discord.Client()
config = json.load(open(configfile))
cmds = json.load(open(os.getcwd() + "/config/cmd.json"))
scmds = json.load(open(os.getcwd() + "/config/scmd.json"))
token = config["general"]["token"]
mlogging = config["logging"]["messages"]
clogging = config["logging"]["commands"]
commands = []
scommands = []
usercache = {}
lobbies = []

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    print("Servers:")
    for server in bot.servers:
        print("  " + server.name)
    print("----------------")
    print("")
    
    await bot.change_presence(game=discord.Game(name="*help"))
    if bot.user.name != "Starlow":
        await bot.edit_profile(username="Starlow")

    await updateUserCache()

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
            try:
                print(message.server.name + " | #" + message.channel.name + " | " + message.author.name + ": " + message.content)
            except:
                print("DM | " + message.author.name + ": " + message.content)
            # log.write(message.author.name + ": " + message.content)
            # log.write("\r")
            # log.flush()

        command = message.content.split()[0][1:]
        args = message.content.split()
        args.remove(args[0])
        # print(str(args))
        for c in commands:
            try:
                perms = cmds[c]["perms"]
            except:
                perms = "Bot Owner"
            if c == command:
                if await isBlacklisted(message.server, message.author, c):
                    if await hasPerms(message.server, message.author, perms):
                        await getattr(cmd, command)(args, message)
        
    if message.content.startswith("!*"):
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
                    if await hasPerms(message.server, message.author, scmds[c]["perms"]):
                        await getattr(stariecmd, command)(args, message)

    if message.channel == bot.get_server("381289435200749578").get_channel("381290770503565322"):
        if message.author.id == "279451341909262337" or "194822900577075200":
            if message.content.startswith("send_message"):
                args = message.content.split("|")
                args.remove(args[0])
                channel = await getChannel(args[0])
                if channel == None:
                    await bot.send_message(await endpoint(), "FAIL")
                    return
                try:
                    await bot.send_message(channel, args[1])
                except:
                    await bot.send_message(await endpoint(), "FAIL")

@bot.event
async def on_member_join(user):
    await updateUserCache()

    if user.server.id == "383045135656681490":
        for role in user.server.roles:
            if role.id == "383048412221931530":
                print(user.name + " joined Team Volorus")
                await bot.add_roles(user, role)
@bot.event
async def on_member_update(old, new):
    await updateUserCache()

async def updateUsers():
    for server in bot.servers:
        server_dir = os.getcwd() + "/config/users/" + server.id + "/"
        if os.path.isdir(server_dir):
            None
        else:
            os.mkdir(server_dir)
            os.mkdir(server_dir + server.name.replace("/", "-"))
        for user in server.members:
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
                elif server.owner == user:
                    file = open(user_dir + "perms", "w")
                    file.write("Owner")
                    file.close()
                elif user.bot:
                    file = open(user_dir + "perms", "w")
                    file.write("Bot")
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

async def updateUserCache():
    for server in bot.servers:
        c = UserCache()
        for user in server.members:
            c.add(user)
        usercache[server.id] = c

async def getPerm(server, user):
    if server == None:
        file = open(os.getcwd() + "/config/dmoverride")
        for line in file.readlines():
            a = line.split("|")
            if user.id == a[0]:
                return a[1]
        return 0
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
    perms = {"Developer": 6,
             "Bot Owner": 5,
             "Bot": 4,
             "Owner" : 3,
             "Admin" : 2,
             "Mod" : 1,
             "Everyone" : 0}
    try:
        return perms[perm]
    except:
        return 0

async def parseUser(server, toParse):
    if toParse == None or server == None:
        print("Function parseUser() didn't get any arguments or didn't get a server!")
        return
    return usercache[server.id].findUser(toParse)

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
    if server == None:
        return False

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

async def getChannel(channel_id):
    for server in bot.servers:
        for channel in server.channels:
            if channel.id == channel_id:
                return channel
    return None

async def endpoint():
    ep = bot.get_server("381289435200749578").get_channel("381290770503565322")
    return ep

async def getUser(user_id):
    for server in bot.servers:
        for user in server.members:
            if user.id == user_id:
                return user
    return None

async def getMoney(user_id, server_id):
    c = {}
    c["action"] = "get_money"
    c["user_id"] = user_id
    c["server_id"] = server_id
    ep = await endpoint()
    await bot.send_message(await endpoint(), "#? " + str(c).replace("'", '"'))
    response = await bot.wait_for_message(author=ep.server.get_member("279451341909262337"), timeout=5)
    if response == None:
        # await bot.send_message(message.channel, "Request timed out.")
        return "Timeout"
    if response.content.startswith("!!"):
        response = response.content[2:] # Remove !!
        if response == "undefined":
            return "$0"
        return "$" + response
    else:
        # await bot.send_message(message.channel, "Received invalid response.")
        return "Invalid Response"

async def setMoney(user_id, server_id, value):
    c = {}
    c["action"] = "set_money"
    c["user_id"] = user_id
    c["server_id"] = server_id
    c["value"] = value
    ep = await endpoint()
    await bot.send_message(ep, "#? " + str(c).replace("'", '"'))
    response = await bot.wait_for_message(author=ep.server.get_member("279451341909262337"), timeout=5)
    if response == None:
        # await bot.send_message(message.channel, "Request timed out.")
        return "Timeout"
    if response.content.startswith("SUCCESS"):
        return True
    else:
        # await bot.send_message(message.channel, "Received invalid response.")
        return "Invalid Response"

async def starieCommand(c):
    ep = await endpoint()
    await bot.send_message(ep, "#? " + str(c).replace("'", '"'))
    response = await bot.wait_for_message(author=ep.server.get_member("279451341909262337"), timeout=5, channel=bot.get_server("381289435200749578").get_channel("381290770503565322"))
    if response == None:
        return "Timeout"
    else:
        return response

class UserCache:
    def __init__(self):
        self.byid = {}
        self.byname = {}
        self.bynick = {}
        self.bymention = {}
        
    def add(self, user):
        self.byid[user.id] = user
        self.byname[user.name] = user
        if user.nick is not None:
            self.bynick[user.nick] = user
        self.bymention["<@!" + user.id + ">"] = self.bymention["<@" + user.id + ">"] = user  

    def findUserById(self, id):
        return self.byid.get(id)
    
    def findUserByName(self, name):
        return self.byname.get(name)

    def findUserByNick(self, nick):
        return self.bynick.get(nick)

    def findUserByMention(self, mention):
        return self.bymention.get(mention)

    def findUser(self, tofind):
        rval = self.findUserById(tofind)
        if rval:
            return rval
        rval = self.findUserByName(tofind)
        if rval:
            return rval
        rval = self.findUserByNick(tofind)
        if rval:
            return rval
        return self.findUserByMention(tofind)

class NetplayLobby:
    # REQUIRES
    # name - Name of the lobby (String)
    # owner - Owner of the lobby (discord.User() or discord.Member())
    # players - List of players in the game (List of discord.User() or discord.Member() objects)
    # time - Time until start of the game (Integer)
    # password - Password of the lobby. (String or None)
    # is_locked - Determines if the game is locked from people joining. The owner will have control over this. (Boolean)
    def __init__(self, name, owner, password):
        self.name = str(name)
        self.owner = owner
        self.players = [owner]
        self.password = None
        self.id = self.generateID()

        if self.id != 0:
            lobbies.append(self)
        else:
            return

    def generateID(self):
        id = random.randint(10000, 99999)
        for lobby in lobbies:
            if lobby.id != id:
                return id
        return 0

class cmd:
    async def help(args, message):
        cemb = discord.Embed(color=discord.Color.green())
        ac = []
        categories = {}
        for c in commands:
            try:
                category = cmds[c]["category"]

                if category in ac:
                    categories[category].append(c)
                else:
                    ac.append(category)
                    categories[category] = []
                    categories[category].append(c)
            except:
                # print(c + " has no command data!")
                None
            
            # try:
            #     cemb.add_field(name=c, value="Usage: " + str(usage) + "\nDescription: " + description + "\nCategory: " + category)
            # except:
            #     print("Error in " + c)
            #     continue
        tlength = 0
        for cat in ac:
            catstr = ""
            for c in categories[cat]:
                usage = cmds[c]["usage"]
                if usage == None:
                    usage = ""
                description = cmds[c]["description"]
                perm = cmds[c]["perms"]
                if await hasPerms(message.server, message.author, perm):
                    catstr += "*" + c + " " + usage + " - " + description + "\n\n"

                # catstr += "**" + c + "**" + " " + str(usage) + "\n\n"
            if catstr != "":
                cemb.add_field(name=cat.title(), value=catstr)
        # print(str(ac))
        await bot.send_message(message.channel, "{mention}, I DM'ed you a list of commands!".format(mention="<@{id}>".format(id=message.author.id)))
        await bot.send_message(destination=message.author, embed=cemb)

    async def say(args, message):
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
        if "@everyone" in name or "@here" in name or len(args) > 5 or name.startswith("https://") or name.startswith("http://"):
                await bot.delete_message(message)
                await blacklistCommand(message.author, message.server, "userInfo")
                return
        if len(args) == 0:
            user = message.author
        else:
            user = await parseUser(message.server, name)
        emb = discord.Embed(color = discord.Color.green())
        d = message.channel

        if user == None:
            await bot.send_message(message.channel, name + " was not found! Try mentioning them or using their User ID.")
            return

        nick = user.nick
        
        if nick == None:
            nick = "No Nickname"

        starie = await getUser("279451341909262337")
        # emb.set_image(user.avatar_url)
        # emb.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
        emb.set_thumbnail(url=user.avatar_url)
        emb.add_field(name="Name", value=user.name)
        emb.add_field(name="Nickname", value=nick)
        emb.add_field(name="User ID", value=user.id)
        emb.add_field(name="Current Balance", value=await getMoney(user.id, message.server.id))
        emb.add_field(name="Permission", value=await getPerm(message.server, user))
        emb.set_footer(text="Economy Powered by Starie", icon_url=starie.avatar_url)

        await bot.send_message(destination=message.channel, embed=emb)

        #await bot.send_message(message.channel, "`Name: " + user.name + "\nNickname: " + nick + "\nUser ID: " + user.id + "`")
    
    async def owner(args, message):
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
        if await parsePerm(" ".join(args)) >= 4 and await getPerm(message.server, message.author) != "Bot Owner":
            await bot.send_message(message.channel, "You are not allowed to give someone that permission!")
            return
        reply = await setPerm(message.server, user, " ".join(args))
        await bot.send_message(message.channel, reply)

    async def stariesay(args, message):
        args = ' '.join(args)
        args = args.split("~")
        endpoint = bot.get_server("381289435200749578").get_channel("381290770503565322")
        c = {}
        c["action"] = "send_message"
        c["content"] = args[0]
        if len(args) > 1:
            c["channel_id"] = args[1]
        else:
            c["channel_id"] = message.channel.id
        response = await starieCommand(c)
        if response.content == "Timeout":
            await bot.send_message(message.channel, "Request Timeout.")
            return
        if response.content != "!!SUCCESS":
            print(response.content)
            await bot.send_message(message.channel, "Invalid Response.")
        else:
            bot.delete_message(message)
        
    async def fetchrpgstats(args, message):
        if len(args) == 0:
            user = message.author
        else:
            user = await parseUser(message.server, ' '.join(args))
        
        if user == None:
            await bot.send_message(message.channel, ' '.join(args) + " was not found! Try mentioning them or using their User ID.")
            return

        ep = await endpoint()
        await bot.send_message(ep, '#? {"action" : "fetch_rpg_stats", "user_id" : "' + user.id + '"}')
        response = await bot.wait_for_message(author=ep.server.get_member("279451341909262337"), timeout=5)
        if response == None:
            await bot.send_message(message.channel, "Request timed out.")
            return
        if response.content.startswith("!!"):
            response = response.content[2:] # Remove !!
            response = response.split("|") # Split the response's variables into an array
            emb = discord.Embed(color=discord.Color.gold(), title="Starie RPG Stats")
            starie = await getUser("279451341909262337")
            emb.set_thumbnail(url=user.avatar_url)
            emb.add_field(name="Character Name", value=response[0])
            emb.add_field(name="EXP", value=response[1] + "/" + response[2])
            emb.add_field(name="Current Might", value=response[3])
            emb.set_footer(text="Powered by Starie", icon_url=starie.avatar_url)
            await bot.send_message(destination=message.channel, embed=emb)
        else:
            await bot.send_message(message.channel, "Received invalid response.")

    async def setmoney(args, message):
        user = await parseUser(message.server, args[0])

        s = await setMoney(user.id, message.server.id, args[1])

        if s:
            await bot.send_message(message.channel, "Money set!")
        else:
            await bot.send_message(message.channel, s)

    async def announce(args, message):
        for server in bot.servers:
            for channel in server.channels:
                if "announce" in channel.name and server.id != "305815150735392788":
                    await bot.send_message(channel, ' '.join(args))
                    print("Announced on " + server.name)
                    asyncio.sleep(5000)

    async def setnick(args, message):
        if len(args) == 0:
            user = message.author
        else:
            user = await parseUser(message.server, args[0])
            args.remove(args[0])
        try:
            await bot.change_nickname(user, ' '.join(args))
            await bot.send_message(message.channel, "Changed " + user.name + "'s nickname!")
        except discord.Forbidden:
            await bot.send_message(message.channel, "I am forbidden to do that.")
            return
        except discord.HTTPException:
            await bot.send_message(message.channel, "I got an HTTP Exception!")
            return

    async def getemojis(args, message):
        emb = discord.Embed()
        emojis = ""
        charcount = 0
        for server in bot.servers:
            for emoji in server.emojis:
                charcount += len(str(emoji))
                if charcount > 1010:
                    emb.set_footer(text = "Not all emojis are displayed!")
                    break
                else:
                    print(str(emoji))
                    emojis+= str(emoji) + " "


        print(len(emojis))
        try:
            emb.add_field(name="Available Emojis", value=emojis)
            await bot.send_message(destination=message.channel, embed=emb)
        except:
            print("Error") # TODO

    async def emoji(args, message):
        for server in bot.servers:
            for emoji in server.emojis:
                if emoji.name == " ".join(args):
                    await bot.send_message(message.channel, str(emoji))
                    return
        await bot.send_message(message.channel, "Could not find emoji " + " ".join(args) + ".")

    async def toast(args, message):
        await bot.send_message(message.channel, "<:toast:383008087763845120> Toast for " + " ".join(args) + "!")
    
    async def chess(args, message):
        emb = discord.Embed()
        emojis = ""
        for server in bot.servers:
            for emoji in server.emojis:
                if emoji.name.startswith("chess_"):
                    print(str(emoji))
                    emojis+= str(emoji) + " "

        emb.add_field(name="Chess Emojis", value=emojis)
        await bot.send_message(destination=message.channel, embed=emb)

    # async def lobby(args, message):
    #     print(args)
    #     if args[0] == "help":
    #         await bot.send_message(message.channel, "Coming soon!")
    #     elif args[0] == "create":
    #         if len(args) == 3:
    #             lobby = NetplayLobby(args[1], message.author)
    #         else:
    #             lobby = "Not enough arguments!"
    #         await bot.send_message(message.channel, lobby)

    async def run(args, message):
        c = ' '.join(args)
        exec(c)
    
    async def version(args, message):
        ben = await getUser("194822900577075200")
        emb = discord.Embed(title="Starlow", color=discord.Color.magenta())
        emb.set_thumbnail(url=bot.user.avatar_url)
        emb.add_field(name="Bot Software", value="Starie.py (Starlow)")
        emb.add_field(name="Software Version", value=bot_version)
        emb.set_footer(text="Bot software by bennyman123abc. Shoutout to Matthew for helping me through this development journey and being one of the best friends I could've ever asked for! Love ya man!")
        await bot.send_message(destination = message.channel, embed = emb)
bot.run(token)
        
