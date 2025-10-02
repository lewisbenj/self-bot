import discord
import os
import requests
import time
import asyncio
from discord.ext import commands
import aiohttp
import random
import psutil
from colorama import Fore, Style, init
init(autoreset=True)

# Creator: @benjaminlewis
# Contact info: Discord  @benjaminlewis | youtube @benjaminlewis  | github @benjaminlewis 

# CONFIG
TOKEN = "Dán cái token ở đây"
PREFIX = "?" # Đổi cái nào cũng được nha hihi
intents = discord.Intents.default()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, self_bot=True, intents=intents)

# globals
protection_running = False
protection_messages = []
protection_groupchat = []
protection_tasks = {}
tokens = []

# ASCII HEADERS 
HEADERS = {
    "page1": """[2;31m
╔═════════════════════════════╗
║        CHAT COMMANDS        ║
╚═════════════════════════════╝[0m""",

    "page2": """[2;32m
╔═════════════════════════════╗
║       STATUS COMMANDS       ║
╚═════════════════════════════╝[0m""",

    "page3": """[2;34m
╔═════════════════════════════╗
║      FRIENDS / DM           ║
╚═════════════════════════════╝[0m""",

    "page4": """[2;35m
╔═════════════════════════════╗
║        GROUPCHAT            ║
╚═════════════════════════════╝[0m""",

    "page5": """[2;36m
╔═════════════════════════════╗
║       UTILITY COMMANDS      ║
╚═════════════════════════════╝[0m"""
}

# Biết code thì làm hộ phần này luôn

PAGES = {
    "page1": f"""{HEADERS['page1']}
[2;31m`?pack @user`[0m – Sử dụng gói chửi trong pack.txt  
[2;31m`?death @user`[0m – Sử dụng từ ngữ xúc phạm death.txt  
[2;31m`?court @user`[0m – Roast chửi lại w/ court.txt  
[2;31m`?mock @user`[0m – Sử dụng từ ngữ chế giễu 
[2;31m`?spam <text> <amt>`[0m – Sử dụng gói Spam 
[2;31m`?thrax @user`[0m – Chatpack gói chửi
[2;31m`?pingpack @user`[0m – Ping spam  
[2;31m`?packend`[0m – Dừng chửi
[2;31m`?autopack @user`[0m – Auto chửi 
[2;31m`?packmenu`[0m – Show kiểu pack
[2;31m`?exile @user`[0m – Lưu đày một thằng nigga(op asf) 
[2;31m`?exileoff `[0m – Turn off gói
""",

    "page2": f"""{HEADERS['page2']}
[2;32m`?playing <text>`[0m – Set "Playing..." status  
[2;32m`?stream <text>`[0m – Set "Streaming..." status  
[2;32m`?listening <text>`[0m – Set "Listening to..."  
[2;32m`?watching <text>`[0m – Set "Watching..."  
[2;32m`?clearstatus`[0m – Xóa tất cả sự hiện diện
[2;32m`?statuscycle`[0m – Starts rotating trong status.txt  
[2;32m`?statusstop`[0m – Dừng trạng thái tuần hoàn 
[2;32m`?customstatus <emoji> <text>`[0m – Set custom  
[2;32m`?fakegame <text>`[0m – Fake game  
[2;32m`?richstatus`[0m – Sự hiện diện phong phú lạ mắt? (soon)  
""",

    "page3": f"""{HEADERS['page3']}
[2;34m`?dm <msg>`[0m – DM cho tất cả bạn bè
[2;34m`?addall`[0m – Thêm bạn bè trong list
[2;34m`?removeall`[0m – Huỷ kết bạn với tất cả
[2;34m`?autoreply @user <msg>`[0m – Auto reply  
[2;34m`?autoreact @user <emoji>`[0m – Auto react  
[2;34m`?massreact <emoji>`[0m – React to all messages  
[2;34m`?reactstop`[0m – Stop auto reactions  
[2;34m`?dmlog`[0m – Log who was DMed  
[2;34m`?dmstop`[0m – Stop DMing  
[2;34m`?massblock`[0m – Block all friends  
""",

    "page4": f"""{HEADERS['page4']}
[2;35m`?gcfill`[0m – Add tokens to GC  
[2;35m`?gckill @user`[0m – Token spam @user  
[2;35m`?gcspam <msg>`[0m – GC spam  
[2;35m`?gcrename`[0m – Rename GC repeatedly  
[2;35m`?gcname <name>`[0m – Set GC name  
[2;35m`?gckick @user`[0m – Kick user from GC  
[2;35m`.protection`[0m – Use protection.txt for renames  
[2;35m`.antiraid`[0m – Lockdown chat  
[2;35m`.shieldon`[0m – Auto delete raids  
[2;35m`.shieldoff`[0m – Turn off shield  
""",

    "page5": f"""{HEADERS['page5']}
[2;36m`?ping`[0m – Show ping  
[2;36m`?uptime`[0m – Show uptime  
[2;36m`?restart`[0m – Restart bot  
[2;36m`?shutdown`[0m – Exit selfbot  
[2;36m`?tokeninfo`[0m – Token details  
[2;36m`?whois <@user>`[0m – Info on user  
[2;36m`?serverinfo`[0m – Info on server  
[2;36m`?userinfo @user`[0m – User details  
[2;36m`?snipe`[0m – Last deleted msg  
[2;36m`?editsnipe`[0m – Last edit  
"""
}


@bot.event
async def on_ready():
  

    # token counter cuz why not
    token_count = 0
    if os.path.exists("tokens.txt"):
        with open("tokens.txt", "r") as f:
            token_count = len([line.strip() for line in f if line.strip()])
    if token_count == 0:
        token_count = 1

    # friend count (if possible i tried)
    try:
        friends = len(await bot.user.relationships())
    except:
        friends = "N/A"

    guilds = len(bot.guilds)

    ascii_art = f"""{Fore.MAGENTA}
███╗░░██╗░██████╗░██╗░░░██╗██╗░░░██╗███████╗███╗░░██╗
████╗░██║██╔════╝░██║░░░██║╚██╗░██╔╝██╔════╝████╗░██║
██╔██╗██║██║░░██╗░██║░░░██║░╚████╔╝░█████╗░░██╔██╗██║
██║╚████║██║░░╚██╗██║░░░██║░░╚██╔╝░░██╔══╝░░██║╚████║
██║░╚███║╚██████╔╝╚██████╔╝░░░██║░░░███████╗██║░╚███║
╚═╝░░╚══╝░╚═════╝░░╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚══╝
{Style.RESET_ALL}
"""
# làm ngầu ngầu vậy thôi chứ muốn đổi cái gì cũng được

    print(ascii_art)
    print(f"{Fore.CYAN}[+] Logged in as:{Style.RESET_ALL} {bot.user}")
    print(f"{Fore.MAGENTA}[+] Prefix:{Style.RESET_ALL} ?")
    print(f"{Fore.MAGENTA}[+] Friends:{Style.RESET_ALL} {friends}")
    print(f"{Fore.MAGENTA}[+] Servers:{Style.RESET_ALL} {guilds}")
    print(f"{Fore.MAGENTA}[+] Tokens Running:{Style.RESET_ALL} {token_count}")
    print(f"{Fore.MAGENTA}[+] Creator:{Style.RESET_ALL} @Benjamin Lewis")


# Page Commands | Có đổi lại thì nhớ đổi luôn cái ở dưới nha
@bot.command()
async def page1(ctx):
    await ctx.send(f"```ansi\n{PAGES['page1']}```")


@bot.command()
async def page2(ctx):
    await ctx.send(f"```ansi\n{PAGES['page2']}```")

@bot.command()
async def page3(ctx):
    await ctx.send(f"```ansi\n{PAGES['page3']}```")

@bot.command()
async def page4(ctx):
    await ctx.send(f"```ansi\n{PAGES['page4']}```")

@bot.command()
async def page5(ctx):
    await ctx.send(f"```ansi\n{PAGES['page5']}```")


HEADERS.update({
    "page6": """[2;35m
╔═════════════════════════════╗
║         TROLL TOOLS         ║
╚═════════════════════════════╝[0m""",

    "page7": """[2;33m
╔═════════════════════════════╗
║          WEBHOOK            ║
╚═════════════════════════════╝[0m""",

    "page8": """[2;36m
╔═════════════════════════════╗
║        ACCOUNT TOOLS        ║
╚═════════════════════════════╝[0m""",

    "page9": """[2;92m
╔═════════════════════════════╗
║           GAMES             ║
╚═════════════════════════════╝[0m""",

    "page10": """[2;91m
╔═════════════════════════════╗
║       EXPLOIT TOOLS         ║
╚═════════════════════════════╝[0m"""
})

# Biết code thì code luôn phần này hộ tôi, tôi cảm ơn
PAGES.update({
    "page6": f"""{HEADERS['page6']}
[2;35m`?rickroll @user`[0m – Send rickroll (corny)  
[2;35m`?fakeban @user`[0m – Fake ban   
[2;35m`?trollping @user`[0m – Ping spam  
[2;35m`?ip @user`[0m – Fake IP leak  
[2;35m`?hacked @user`[0m – Fake hack script  
[2;35m`?clown @user`[0m – Reacts 🧢 🤡  
[2;35m`?weirdify <text>`[0m – 𝖜𝖊𝖎𝖗𝖉 𝖙𝖊𝖝𝖙  
[2;35m`?uwu <text>`[0m – UWUfy text  
[2;35m`?corny @user`[0m – corny  
[2;35m`?ghostping @user`[0m – Ping then delete  
""",

    "page7": f"""{HEADERS['page7']}
[2;33m`?whspam <url> <msg> <amt>`[0m – Spam webhook  
[2;33m`?whdelete <url>`[0m – Delete webhook  
[2;33m`?whnuke <url> <amt>`[0m – Nuke via webhook  
[2;33m`?whflood <url>`[0m – Loop messages  
[2;33m`?whhook <name> <msg>`[0m – Fancy webhook  
[2;33m`?whrainbow <url>`[0m – Color spam  
[2;33m`?whghost <url>`[0m – Ghost pings  
[2;33m`?whupload <url>`[0m – File spam  
[2;33m`?whspamlist`[0m – Use list of webhooks  
[2;33m`?whmassdelete`[0m – Delete list of webhooks  
""",

    "page8": f"""{HEADERS['page8']}
[2;36m`?resetpfp`[0m – Clears avatar  
[2;36m`?resetbio`[0m – Clears about me  
[2;36m`?setbio <text>`[0m – Set about me  
[2;36m`?setpfp <url>`[0m – Set profile pic  
[2;36m`?setbanner <url>`[0m – Banner image  
[2;36m`?nick <name>`[0m – Change nickname  
[2;36m`?cloneme`[0m – Clone another profile  
[2;36m`?namehistory @user`[0m – Username logs  
[2;36m`?badgegrab @user`[0m – Show badges  
[2;36m`?accountage`[0m – Show account creation  
""",

"page9": f"""{HEADERS['page9']}
[2;32m`?coinflip`[0m – Heads or tails  
[2;32m`?roll`[0m – Roll dice  
[2;32m`?slots`[0m – Play slot machine  
[2;32m`?rps <rock/paper/scissors>`[0m – RPS battle  
[2;32m`?8ball <question>`[0m – Magic 8-ball  
[2;32m`?gayrate @user`[0m – 0–100% gay  
[2;32m`?simprate @user`[0m – 0–100% simp  
[2;32m`?ppsize @user`[0m – Peepee size meter  
[2;32m`?truth`[0m – Truth question  
[2;32m`?dare`[0m – Dare challenge  
""",


"page10": f"""{HEADERS['page10']}
[2;31m`?massleave`[0m – Leave all servers  
[2;31m`?massdm <msg>`[0m – DM all servers  
[2;31m`?massreact <emoji>`[0m – Spam reacts  
[2;31m`?stealemoji <url>`[0m – Upload emoji  
[2;31m`?leaktokens`[0m – Show grabbed tokens  
[2;31m`?grabip`[0m – Show public IP  
[2;31m`?webping <url>`[0m – Ping website  
[2;31m`?ddos <ip>`[0m – Fake DDoS (visual only)  
[2;31m`?killselfbot`[0m – Self destruct  
[2;31m`?grabberlink`[0m – Sends link with logger  
""",

})


HEADERS.update({
    "page11": """[2;91m
╔═════════════════════════════╗
║      DISCORD RAID           ║
╚═════════════════════════════╝[0m""",

    "page12": """[2;95m
╔═════════════════════════════╗
║     MESSAGE MODIFIERS       ║
╚═════════════════════════════╝[0m""",

    "page13": """[2;96m
╔═════════════════════════════╗
║      ANIMATED SPAM          ║
╚═════════════════════════════╝[0m""",

    "page14": """[2;92m
╔═════════════════════════════╗
║      AI / GENERATION        ║
╚═════════════════════════════╝[0m""",

    "page15": """[2;37m
╔═════════════════════════════╗
║      MISC COMMANDS          ║
╚═════════════════════════════╝[0m"""
})


PAGES.update({
"page11": f"""{HEADERS['page11']}
[2;33m`?nuke`[0m – Delete channels & spam  
[2;33m`?spamchannels <name>`[0m – Mass create channels  
[2;33m`?spamroles <name>`[0m – Mass create roles  
[2;33m`?deleteroles`[0m – Delete all roles  
[2;33m`?deletechannels`[0m – Delete all channels  
[2;33m`?deletemojis`[0m – Delete all emojis  
[2;33m`?deletewebhooks`[0m – Delete all webhooks  
[2;33m`?massban @everyone`[0m – Ban all users  
[2;33m`?masskick`[0m – Kick all users  
[2;33m`?dmall <msg>`[0m – DM everyone in server  
""",


"page12": f"""{HEADERS['page12']}
[2;35m`?reverse <text>`[0m – Reverse message  
[2;35m`?bold <text>`[0m – Bolded version  
[2;35m`?italic <text>`[0m – Italic version  
[2;35m`?underline <text>`[0m – Underlined version  
[2;35m`?strikethrough <text>`[0m – ~~Strike~~ version  
[2;35m`?spoiler <text>`[0m – ||Spoiler|| version  
[2;35m`?zalgify <text>`[0m – ZALGO TEXT  
[2;35m`?cursive <text>`[0m – 𝓒𝓾𝓻𝓼𝓲𝓿𝓮  
[2;35m`?tinytext <text>`[0m – Small caps  
[2;35m`?spongebob <text>`[0m – aLtErNaTiNg caps  
""",

"page13": f"""{HEADERS['page13']}
[2;36m`?emojiflood <emoji>`[0m – Spam emoji wall  
[2;36m`?pingscroll @user`[0m – Ping user vertically  
[2;36m`?wave @user`[0m – Wave animation  
[2;36m`?bomb @user`[0m – Bomb emoji animation  
[2;36m`?fireworks @user`[0m – Firework spam  
[2;36m`?matrix`[0m – Matrix-style spam  
[2;36m`?rainbowtext <msg>`[0m – letters  
[2;36m`?scrollingtext <msg>`[0m – Scroll effect  
[2;36m`?animstatus`[0m – Animated rotating status  
[2;36m`?thunder @user`[0m – spam  
""",


"page14": f"""{HEADERS['page14']}
[2;34m`?aiquote`[0m – Generate fake quote  
[2;34m`?chatgpt <prompt>`[0m – Ask AI  
[2;34m`?nickgpt`[0m – Generate funny nickname  
[2;34m`?packgpt @user`[0m – AI-generated Chatpack  
[2;34m`?aipickup`[0m – AI pickup line  
[2;34m`?aitroll`[0m – AI insult  
[2;34m`?roastme`[0m – Chatpack yourself  
[2;34m`?storygen`[0m – Make a story  
[2;34m`?copypasta`[0m – Generate copypasta  
[2;34m`?promptme`[0m – Random AI prompt  
""",


"page15": f"""{HEADERS['page15']}
[2;37m`?countdown <sec>`[0m – Countdown timer  
[2;37m`?bored`[0m – Suggest something to do  
[2;37m`?remind <sec> <msg>`[0m – Reminder  
[2;37m`?say <text>`[0m – Say anything  
[2;37m`?echo <text>`[0m – Echo back  
[2;37m`?convert <num>`[0m – Binary, hex, etc  
[2;37m`?math <expr>`[0m – Calculator  
[2;37m`?calc <expression>`[0m – Same as math  
[2;37m`?define <word>`[0m – Dictionary lookup  
[2;37m`?translate <lang> <text>`[0m – Translate text  
"""

})


# Page 6–10 rồi nè
@bot.command()
async def page6(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page6']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page7(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page7']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page8(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page8']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page9(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page9']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis:: {e}")

@bot.command()
async def page10(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page10']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

# Page 11–15 are you a skid?
@bot.command()
async def page11(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page11']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page12(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page12']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page13(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page13']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page14(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page14']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def page15(ctx):
    try:
        await ctx.send(f"```ansi\n{PAGES['page15']}```")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")


    


# ========== PAGE 1: CHAT COMMANDS  ========== 

@bot.command()
async def pack(ctx, user: discord.User):
    try:
        with open("pack.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            await ctx.send(f"{line.strip()} {user.mention}")
            await asyncio.sleep(0.5)
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")


@bot.command()
async def death(ctx, user: discord.User):
    try:
        with open("death.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            await ctx.send(f"{user.mention} {line.strip()}")
            await asyncio.sleep(0.5)
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def court(ctx, user: discord.User):
    try:
        with open("court.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            await ctx.send(f"{user.mention} {line.strip()}")
            await asyncio.sleep(0.5)
    except Exception as e:
        await ctx.send(f"error: {e}")

@bot.command()
async def mock(ctx, user: discord.User):
    def to_mock(text):
        return ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))

    def check(msg): return msg.author == user

    await ctx.send(f"lewis sẽ mocking ngay bây giờ {user.name}...")

    @bot.event
    async def on_message(message):
        if message.author == user:
            mocked = to_mock(message.content)
            await message.channel.send(f"{user.mention} {mocked}")

@bot.command()
async def spam(ctx, *, message_and_amount):
    try:
        args = message_and_amount.split()
        if len(args) < 2:
            await ctx.send("Usage: ?spam <message1,message2,etc> <amount>")
            return

        # this splits the messages and amount (op asf for spamming)
        amount = int(args[-1])
        raw_messages = " ".join(args[:-1])
        message_list = raw_messages.split(",")

        await ctx.message.delete()

        channel_id = ctx.channel.id
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        to_send = []
        for i in range(amount):
            message_to_send = message_list[i % len(message_list)]
            to_send.append(message_to_send)

        for message in to_send:
            while True:
                response = requests.post(url, headers=headers, json={"content": message})

                if response.status_code == 429:
                    # rate limit hit nigga wait
                    retry_after = response.json().get("retry_after", 1)
                    print(f"[!] Rate đã đạt đến giới hạn. Hãy đợi trong vòng {retry_after} vài giây...")
                    time.sleep(retry_after)
                else:
                    # sent
                    break

    except Exception as e:
        print(f"Đã có lỗi khi spam: {e}")

@bot.command()
async def thrax(ctx, user: discord.User):
    try:
        with open("thrax.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            await ctx.send(f"{user.mention} {line.strip()}")
            await asyncio.sleep(0.5)
    except Exception as e:
        await ctx.send(f"error in lewis: {e}")

@bot.command()
async def pingpack(ctx, user: discord.User):
    try:
        with open("pack.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            await ctx.send(f"{user.mention} {line.strip()}")
            await asyncio.sleep(0.3)
    except Exception as e:
        await ctx.send(f"error: {e}")

@bot.command()
async def packend(ctx):
    await ctx.send("lewis has now stopped packing.")

@bot.command()
async def autopack(ctx, user: discord.User):
    await ctx.send(f"lewis selfbot auto pack :3 {user.name}...")

    async def auto():
        try:
            with open("pack.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            while True:
                for line in lines:
                    await ctx.send(f"{user.mention} {line.strip()}")
                    await asyncio.sleep(1)
        except Exception as e:
            await ctx.send(f"error: {e}")

    bot.loop.create_task(auto())

@bot.command()
async def packmenu(ctx):
    await ctx.send("**chat packing options xd:**\n- `?pack @user` — Basic\n- `?death @user` — Execution\n- `?court @user` — Take that nigga to court\n- '?exile @user ` - ?thrax @user` — @fanciers")

# ========== PAGE 2: STATUS COMMANDS ==========

status_task = None

@bot.command()
async def playing(ctx, *, text):
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.send(f"lewis set  status to playing heh **{text}**")

@bot.command()
async def stream(ctx, *, text):
    activity = discord.Streaming(name=text, url="https://twitch.tv/discord")
    await bot.change_presence(activity=activity)
    await ctx.send(f"lewis set stauts to streaming heh **{text}**")

@bot.command()
async def watching(ctx, *, text):
    activity = discord.Activity(type=discord.ActivityType.watching, name=text)
    await bot.change_presence(activity=activity)
    await ctx.send(f"lewis đã được set tại to: watching **{text}**")

@bot.command()
async def listening(ctx, *, text):
    activity = discord.Activity(type=discord.ActivityType.listening, name=text)
    await bot.change_presence(activity=activity)
    await ctx.send(f"lewis đã được set tại to: listening to **{text}**")

@bot.command()
async def clearstatus(ctx):
    await bot.change_presence(activity=None)
    await ctx.send("lewis presence cleared.")

@bot.command()
async def statuscycle(ctx):
    global status_task
    if status_task:
        await ctx.send("lewis status cycling already running.")
        return

    async def cycle():
        global status_task
        try:
            while True:
                with open("status.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        await bot.change_presence(activity=discord.Game(name=line.strip()))
                        await asyncio.sleep(10)
        except:
            pass

    status_task = bot.loop.create_task(cycle())
    await ctx.send("lewis  status cycling started from `status.txt`.")

@bot.command()
async def statusstop(ctx):
    global status_task
    if status_task:
        status_task.cancel()
        status_task = None
        await ctx.send("lewis SELFBOT status cycling is now off")
    else:
        await ctx.send("lewis SELFBOT no status cycling running.")

@bot.command()
async def customstatus(ctx, emoji, *, text):
    try:
        await bot.change_presence(activity=discord.CustomActivity(name=text, emoji=emoji))
        await ctx.send(f"custom status is set to: {emoji} {text}")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis:: {e}")

@bot.command()
async def fakegame(ctx, *, text):
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.send(f"lewis SELFBOT Fake game đã được set tại: **{text}**")

@bot.command()
async def richstatus(ctx):
    await ctx.send("lewis SELFBOT Rich Presence coming soon. (Do stream or customstatus etc to get an rpc.)")


# ========== PAGE 3: FRIENDS / DM / AUTO  ==========                                                    >_<

from itertools import islice


autoreply_tasks = {}
autoreact_targets = {}

@bot.command()
async def dm(ctx, *, msg):
    await ctx.send("```lewis mass dm, dming all your friends (if you get phone locked dont blame me this can get you limited)```")
    try:
        friends = bot.user.friends  # <--  so it can dm ur friends cause my dumb ass forgot to add this in before i put this note here to remember s

        total_sent = 0
        failed_sent = 0

        batch_size = 5
        delay_between_batches = 5

        for i in range(0, len(friends), batch_size):
            batch = friends[i:i+batch_size]

            for friend in batch:
                try:
                    formatted_msg = f"```ansi\n\u001b[2;36m{msg}\u001b[0m```"  # Cyan box color twin
                    await friend.send(formatted_msg)
                    print(f"[+] DM sent to {friend.name}")
                    total_sent += 1
                except Exception as e:
                    print(f"[!] Could not DM {friend.name}: {e}")
                    failed_sent += 1

            await asyncio.sleep(delay_between_batches)

        await ctx.send(f"```lewis mass has been done\nSent: {total_sent}\nFailed: {failed_sent}```")

    except Exception as e:
        await ctx.send(f"```Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}```")


@bot.command()
async def addall(ctx):
    await ctx.send("WIP (coming soon to lewis im lazy and its hard) — Add friend IDs from file soon.")

@bot.command()
async def removeall(ctx):
    await ctx.send("lewis is now removing all your nonexisting friends...")

    try:
        friends = await bot.user.relationships()
        for f in friends:
            try:
                await f.delete()
                await asyncio.sleep(1)
            except:
                pass
        await ctx.send("lewis selfbot unfriended all.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def autoreply(ctx, user: discord.User, *, msg="Hello."):
    channel_id = ctx.channel.id
    autoreply_tasks[user.id] = msg
    await ctx.send(f"lewis autoreplying to {user.name} with: `{msg}`")

@bot.command()
async def autoreact(ctx, user: discord.User, emoji):
    autoreact_targets[user.id] = emoji
    await ctx.send(f"lewis is now reacting to {user.name} with {emoji}")

@bot.command()
async def reactstop(ctx):
    autoreact_targets.clear()
    await ctx.send("lewis auto react is now off.")

@bot.command()
async def dmlog(ctx):
    await ctx.send("lewis  WIP — future logging to file.")

@bot.command()
async def dmstop(ctx):
    global dm_tasks
    dm_tasks.clear()
    await ctx.send("lewis dm tasks have now stapped.")

@bot.command()
async def massblock(ctx):
    await ctx.send("lewis blocking all of your friends CLOSE THE BOT IF U WANNA CANCEL THIS...")
    try:
        friends = await bot.user.relationships()
        for f in friends:
            try:
                await f.block()
                await asyncio.sleep(1)
            except:
                pass
        await ctx.send("lewis You Blocked all friends (time to get off discord and actually do something cool).")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

#  listener for auto-reply/react | are you a skid?
@bot.event
async def on_message(message):
    if message.author.id in autoreply_tasks:
        try:
            await message.channel.send(f"{message.author.mention} {autoreply_tasks[message.author.id]}")
        except: pass

    if message.author.id in autoreact_targets:
        try:
            await message.add_reaction(autoreact_targets[message.author.id])
        except: pass

    await bot.process_commands(message)


# ========== PAGE 4: GROUPCHAT  ========== #                                 ^_^



@bot.command()
async def gcfill(ctx):
    try:
        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        await ctx.send("`tokens.txt` không tồn tại.")
        return

    headers = {
        "Authorization": bot.http.token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    added = 0

    for token in tokens[:12]:  # Add first 12
        try:
            # Get user ID from token
            user_data = requests.get(
                "https://discord.com/api/v9/users/@me",
                headers={"Authorization": token}
            )

            if user_data.status_code != 200:
                print(f"[!] Could not get user from token ending {token[-4:]}")
                continue

            user_id = user_data.json()["id"]

            # Add to GC
            url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/recipients/{user_id}"
            res = requests.put(url, headers=headers)

            if res.status_code == 204:
                print(f"[+] Added {user_id}")
                added += 1
            else:
                print(f"[!] Failed to add {user_id} — Status {res.status_code}")
            await asyncio.sleep(1.25)

        except Exception as e:
            print(f"[!] Error: {e}")

    await ctx.send(f"lewis tried adding {added}/{len(tokens[:12])} users to the group.")


        





@bot.command()
async def exile(ctx, user: discord.User):
    global protection_running
    protection_running = True
    channel_id = ctx.channel.id

    try:
        with open("tokens.txt", "r") as f:
            tokens = [line.strip() for line in f if line.strip()]
    except:
        await ctx.send("`tokens.txt` missing.")
        return

    try:
        with open("protection.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            protection_messages = lines
            protection_groupchat = lines
    except:
        await ctx.send("`protection.txt` missing.")
        return

    class SharedCounter:
        def __init__(self):
            self.value = 1
            self.lock = asyncio.Lock()

        async def increment(self):
            async with self.lock:
                current = self.value
                self.value += 1
                return current

    shared_counter = SharedCounter()

    async def send_message(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        last_send_time = 0
        backoff_time = 0.1

        while protection_running:
            try:
                current_time = time.time()
                time_since_last = current_time - last_send_time
                if time_since_last < backoff_time:
                    await asyncio.sleep(backoff_time - time_since_last)

                message = random.choice(protection_messages)
                count = await shared_counter.increment()

                payload = {
                    'content': f"{message} {user.mention}\n```{count}```"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            print(f"[+] Message sent by {token[-4:]}")
                            last_send_time = time.time()
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"[!] Rate limit {token[-4:]} for {retry_after}s")
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"[!] Failed to send with {token[-4:]} — {resp.status}")
                            await asyncio.sleep(1)

                await asyncio.sleep(random.uniform(0.2, 0.5))

            except Exception as e:
                print(f"[!] Error in message task ({token[-4:]}): {e}")
                await asyncio.sleep(1)

    async def change_name(token):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        last_change_time = 0
        backoff_time = 0.5

        while protection_running:
            try:
                current_time = time.time()
                time_since_last = current_time - last_change_time
                if time_since_last < backoff_time:
                    await asyncio.sleep(backoff_time - time_since_last)

                gc_name = random.choice(protection_groupchat)
                count = await shared_counter.increment()

                payload = {
                    'name': f"{gc_name} {count}"
                }

                async with aiohttp.ClientSession() as session:
                    async with session.patch(
                        f'https://discord.com/api/v9/channels/{channel_id}',
                        headers=headers,
                        json=payload
                    ) as resp:
                        if resp.status == 200:
                            print(f"[+] GC name changed by {token[-4:]}")
                            last_change_time = time.time()
                        elif resp.status == 429:
                            retry_after = float((await resp.json()).get('retry_after', 1))
                            print(f"[!] Name rate limit {token[-4:]}: {retry_after}s")
                            await asyncio.sleep(retry_after)
                        else:
                            print(f"[!] Name change failed for {token[-4:]} — {resp.status}")
                            await asyncio.sleep(1)

                await asyncio.sleep(random.uniform(0.5, 1.0))

            except Exception as e:
                print(f"[!] Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: ({token[-4:]}): {e}")
                await asyncio.sleep(1)

    message_tasks = [send_message(token) for token in tokens]
    name_tasks = [change_name(token) for token in tokens]
    all_tasks = message_tasks + name_tasks

    protection_tasks[channel_id] = asyncio.gather(*all_tasks)
    await ctx.send("i lewis you.")


@bot.command()
async def exileoff(ctx):
    global protection_running
    protection_running = False
    await ctx.send("```exile is now off.```")



@bot.command()
async def gcspam(ctx, *, msg):
    for _ in range(20):
        await ctx.send(msg)
        await asyncio.sleep(0.3)

@bot.command()
async def gcrename(ctx):
    try:
        with open("protection.txt", "r", encoding="utf-8") as f:
            names = f.readlines()

        while True:
            for name in names:
                await ctx.channel.edit(name=name.strip())
                await asyncio.sleep(1)
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def gcname(ctx, *, name):
    try:
        await ctx.channel.edit(name=name)
        await ctx.send(f"LEWIS SELFBOT Group name set to **{name}**")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis:: {e}")

@bot.command()
async def gckick(ctx, user: discord.User):
    try:
        await ctx.channel.send(f"/remove {user.id}")
        await ctx.send(f"lewis has now kicked {user.name} from group.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command(name="protection")
async def _protection(ctx):
    try:
        with open("protection.txt", "r", encoding="utf-8") as f:
            names = f.readlines()

        while True:
            for name in names:
                await ctx.channel.edit(name=name.strip())
                await asyncio.sleep(2)
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def antiraid(ctx):
    await ctx.channel.edit(slowmode_delay=30)
    await ctx.send("lewis anti raid is now on slow mode for 30 seconds")

@bot.command()
async def shieldon(ctx):
    await ctx.send(" auto deletion now active — messages will be purged.")
    @bot.event
    async def on_message(message):
        try:
            if message.channel.id == ctx.channel.id and message.author != bot.user:
                await message.delete()
        except:
            pass
        await bot.process_commands(message)

@bot.command()
async def shieldoff(ctx):
    await ctx.send("shield is now off, messages are no longer gonna be deleted")


# ========== PAGE 5: UTILITY COMMANDS | are you a skid?  ==========

import datetime
import platform
import psutil

start_time = datetime.datetime.utcnow()

@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f"lewis selfbot ping: `{round(latency * 1000)}ms`")

@bot.command()
async def uptime(ctx):
    now = datetime.datetime.utcnow()
    delta = now - start_time
    days, remainder = divmod(int(delta.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"lewis uptime: `{days}d {hours}h {minutes}m {seconds}s`")

@bot.command()
async def restart(ctx):
    await ctx.send("lewis is now restarting...")
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def shutdown(ctx):
    await ctx.send("lewis shutting down.")
    await bot.close()

@bot.command()
async def tokeninfo(ctx):
    user = bot.user
    await ctx.send(f"Token info for **{user}**\nID: `{user.id}`\nTag: `{user}`")

@bot.command()
async def whois(ctx, user: discord.User):
    embed = discord.Embed(title="LEWIS  User Info", color=0x00ffcc)
    embed.add_field(name="Username", value=str(user), inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Created", value=user.created_at.strftime('%Y-%m-%d %H:%M:%S UTC'), inline=False)
    embed.set_thumbnail(url=user.avatar_url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    if ctx.guild:
        embed = discord.Embed(title="LEWIS  Server Info", color=0x00ffcc)
        embed.add_field(name="Name", value=ctx.guild.name, inline=False)
        embed.add_field(name="ID", value=ctx.guild.id, inline=False)
        embed.add_field(name="Owner", value=str(ctx.guild.owner), inline=False)
        embed.add_field(name="Members", value=ctx.guild.member_count, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("LEWIS  This command only works in servers idiot.")

@bot.command()
async def userinfo(ctx, user: discord.User):
    roles = [r.name for r in getattr(user, 'roles', []) if r.name != "@everyone"]
    embed = discord.Embed(title="🧑 User Info", color=0x00ffcc)
    embed.add_field(name="Username", value=str(user), inline=False)
    embed.add_field(name="ID", value=user.id, inline=False)
    embed.add_field(name="Created At", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
    if roles:
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def snipe(ctx):
    await ctx.send("its gonna come soon either in the dev version or the next version idk man join discord.gg/says for updates")

@bot.command()
async def editsnipe(ctx):
    await ctx.send("its gonna come soon either in the dev version or the next version idk man join discord.gg/says for updates") ### whenever i feel like it i'll add it to this. ###

# ========== PAGE 6: TROLL TOOLS | are you a skid?==========

@bot.command()
async def rickroll(ctx, user: discord.User):
    await ctx.send(f"{user.mention} yes im corny asf but check ts out https://youtu.be/dQw4w9WgXcQ")

@bot.command()
async def fakeban(ctx, user: discord.User):
    embed = discord.Embed(
        title="BANNED",
        description=f"User **{user}** has been permanently banned for violating Discord TOS.",
        color=0xff0000
    )
    embed.set_footer(text="Reason: Rape threats, Cuck, and worst of all hes a fucking indian.")
    await ctx.send(embed=embed)

# random shit cause idk what to add sob
@bot.command()
async def trollping(ctx, user: discord.User):
    for _ in range(5):
        await ctx.send(f"{user.mention} 🤡")
        await asyncio.sleep(0.5)

@bot.command()
async def ip(ctx, user: discord.User):
    fake_ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
    await ctx.send(f"IP của người dùng {user.name} là: `{fake_ip}`")

@bot.command()
async def hacked(ctx, user: discord.User):
    await ctx.send(f"💀 {user.name} has been **HACKED** and raped...\nInjecting backdoor with tyrone...\nUpload...\nUploading token to webhook...")
    await asyncio.sleep(3)
    await ctx.send("lewis sucefully hacked")

@bot.command()
async def clown(ctx, user: discord.User):
    await ctx.send(f"{user.mention} 🤡🧢")

@bot.command()
async def weirdify(ctx, *, text):
    weird = ''.join(chr(ord(c) + 0x1D400 - ord('A')) if c.isalpha() else c for c in text.upper())
    await ctx.send(f"{weird}")

@bot.command()
async def uwu(ctx, *, text):
    uwu_text = text.replace("r", "w").replace("l", "w").replace("R", "W").replace("L", "W")
    faces = [" (●´ω｀●)", " owo", " UwU", " >w<", " ^_^"]
    await ctx.send(uwu_text + random.choice(faces))

@bot.command()
async def corny(ctx, user: discord.User):
    slang = [
        "im black",
        "ur blocked n canceled 🤡",
        "ur poor lol",
        "this you? you indian pedophilic fuck",
        "😭",
        "up a band broke dork i run ur shitty com"
    ]
    await ctx.send(f"{user.mention} {random.choice(slang)}")

@bot.command()
async def ghostping(ctx, user: discord.User):
    msg = await ctx.send(f"{user.mention}")
    await asyncio.sleep(0.2)
    await msg.delete()
    await ctx.send("LEWIS ghost pinged.")

# ========== PAGE 7: WEBHOOK (THE BEST UPDATE FOR THIS SELFBOT) | are you a skid? ==========



@bot.command()
async def whspam(ctx, url, *, msg):
    await ctx.send(f"lewis is now spamming the webhook with: `{msg}`")
    try:
        for _ in range(20):
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"content": msg})
            await asyncio.sleep(0.3)
        await ctx.send("lewis webhook spam done xd.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whdelete(ctx, url):
    try:
        async with aiohttp.ClientSession() as session:
            await session.delete(url)
        await ctx.send("webhook deleted.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whnuke(ctx, url, *, msg):
    await ctx.send(f"lewis is now nuking the webhook with `{msg}`shoutout @Benjamin Lewis heh...")
    try:
        for _ in range(50):
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"content": msg})
            await asyncio.sleep(0.1)
        await ctx.send("lewis webhook nuked.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whflood(ctx, url):
    await ctx.send("lewis webhook flooding is now started.")
    try:
        while True:
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"content": "lewis runs me!! 💦"})
            await asyncio.sleep(0.1)
    except:
        pass

@bot.command()
async def whhook(ctx, name, *, msg):
    embed = discord.Embed(title=name, description=msg, color=0x00ffcc)
    async with aiohttp.ClientSession() as session:
        await session.post("YOUR_WEBHOOK_HERE", json={
            "username": name,
            "embeds": [embed.to_dict()]
        })


 # this command is random asf idek
@bot.command()
async def whrainbow(ctx, url):
    await ctx.send("🌈 Rainbow mode started...")
    colors = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]
    try:
        for _ in range(30):
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={"content": random.choice(colors)})
            await asyncio.sleep(0.2)
        await ctx.send("lewis you are now a true faggot.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whghost(ctx, url):
    try:
        msg = {"content": "@everyone"}
        async with aiohttp.ClientSession() as session:
            response = await session.post(url, json=msg)
            if response.status == 204:
                await ctx.send("lewis ghost pinged webhook.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whupload(ctx, url):
    await ctx.send("uploading files to the webhook don't fold")
    try:
        for _ in range(5):
            async with aiohttp.ClientSession() as session:
                await session.post(url, data={"file": open("payload.txt", "rb")})
            await asyncio.sleep(0.3)
        await ctx.send("lewis has sent the files.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def whspamlist(ctx):
    await ctx.send("LEWIS SELFBOT Mass spamming from webhook list not yet added.")

@bot.command()
async def whmassdelete(ctx):
    await ctx.send("LEWIS SELFBOT Mass webhook deletion from list not yet added.")

# ========== PAGE 8: ACCOUNT SHIT CAUSE EVERY SELFBOT NEEDS IT==========
          # === dont be a skid please === #
import requests
from io import BytesIO

@bot.command()
async def resetpfp(ctx):
    await bot.user.edit(avatar=None)
    await ctx.send("lewis selfbot profile picture reset.")

@bot.command()
async def resetbio(ctx):
    headers = {"Authorization": TOKEN}
    json = {"bio": ""}
    try:
        requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=json)
        await ctx.send("lewis bio đã được reset.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def setbio(ctx, *, text):
    headers = {"Authorization": TOKEN}
    json = {"bio": text}
    try:
        requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=json)
        await ctx.send(f"lewis  bio đã được set thành: `{text}`")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def setpfp(ctx, url):
    try:
        img_data = requests.get(url).content
        await bot.user.edit(avatar=img_data)
        await ctx.send("lewis  profile picture updated.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def setbanner(ctx, url):
    await ctx.send("lewis setting banner is locked to Nitro Boost :3—  WIP")

@bot.command()
async def nick(ctx, *, name):
    try:
        await ctx.author.edit(nick=name)
        await ctx.send(f"🪪 Nickname đã được đổi thành: **{name}**")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def cloneme(ctx):
    await ctx.send("lewis note from @Benjamin Lewis: cloning not added yet sorry guys — WIP")

@bot.command()
async def namehistory(ctx, user: discord.User):
    await ctx.send(f"lewis past names of {user.name} not available via user token — WIP")

@bot.command()
async def badgegrab(ctx, user: discord.User):
    flags = user.public_flags
    badges = []
    if flags.staff: badges.append("Staff")
    if flags.partner: badges.append("Partner")
    if flags.hypesquad_balance: badges.append("Balance")
    if flags.hypesquad_bravery: badges.append("Bravery")
    if flags.hypesquad_brilliance: badges.append("Brilliance")
    if flags.verified_bot_developer: badges.append("Dev")
    if flags.bug_hunter: badges.append("Bug Hunter")
    if not badges: badges.append("None")
    await ctx.send(f"badges for {user.name}: {' | '.join(badges)}")

@bot.command()
async def accountage(ctx):
    created = bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    await ctx.send(f"account created on: `{created}`")

# ========== PAGE 9: mini games (im going crazy making this please help) ==========

@bot.command()
async def coinflip(ctx):
    outcome = random.choice(["🪙 Heads", "🪙 Tails"])
    await ctx.send(f"Result: {outcome}")

@bot.command()
async def roll(ctx):
    value = random.randint(1, 6)
    await ctx.send(f"you rolled an **{value}**!")

@bot.command()
async def slots(ctx):
    symbols = ["🍒", "🍋", "🔔", "⭐", "🍇", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    await ctx.send(f"🎰 {' | '.join(result)}")
    if len(set(result)) == 1:
        await ctx.send("You win good job!")
    else:
        await ctx.send("No match try again twin.")

@bot.command()
async def rps(ctx, choice):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    result = ""
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "scissors" and bot_choice == "paper") or \
         (choice == "paper" and bot_choice == "rock"):
        result = "You win (i let you win)"
    else:
        result = "You lost to @Benjamin Lewis haha"
    await ctx.send(f"🪨🧻✂️ You chose `{choice}`, I chose `{bot_choice}` — {result}")

@bot.command()
async def _8ball(ctx, *, question):
    responses = [
        "Yes", "No", "Maybe", "Ask again later", "Definitely", "100%", "Not likely", "Try again", "Doubt it", "hell no"
    ]
    await ctx.send(f"🎱 {random.choice(responses)}")

# LMAOOO
@bot.command()
async def gayrate(ctx, user: discord.User):
    percent = random.randint(0, 100)
    await ctx.send(f"lewis {user.mention} is **{percent}%** gay.")

@bot.command()
async def simprate(ctx, user: discord.User):
    percent = random.randint(0, 100)
    await ctx.send(f"lewis {user.mention} is **{percent}%** simp.")

@bot.command()
async def ppsize(ctx, user: discord.User):
    length = random.randint(0, 15)
    bar = "8" + "=" * length + "D"
    await ctx.send(f"lewis {user.mention}'s PP size:\n`{bar}`")

@bot.command()
async def truth(ctx):
    truths = [
        "Nỗi sợ hãi lớn nhất của mày là gì?", "Mày đã bao giờ đánh cặc của mình để xem phim khiêu dâm chưa?",
        "Mày có đụ em gái của mày để loạn luân không?", "Có buôn bán ma tuý chưa?",
        "Có chịch nhỏ bạn thân mày chưa?"
    ]
    await ctx.send(f"LEWIS Truth: {random.choice(truths)}")
# ion even know
@bot.command()
async def dare(ctx):
    dares = [
        "Nói cho tao biết cách để hành hạ một thằng da đen là gì?", "Cặp vú của nhỏ bồ mày đẹp đấy",
        "Xem sex còn đỡ hơn nói chuyện với mày đấy?", "Hay là mày đổi nghề làm diễn viên phim sex đi?",
        "Xoá mẹ Discord đi, tag quần què tao"
    ]
    await ctx.send(f"LEWIS SELFBOT Dare: {random.choice(dares)}")
# ========== PAGE 10: EXPLOIT SHIT ==========

@bot.command()
async def massleave(ctx):
    await ctx.send("Rời khỏi tất cả các máy cắt nếu bạn muốn dừng việc này, chỉ cần đóng bot hoặc bất cứ thứ gì bạn lưu trữ nó...")
    try:
        for guild in bot.guilds:
            await guild.leave()
            await asyncio.sleep(0.5)
        await ctx.send("lewis đã rời khỏi Server rồi ^_^.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def massdm(ctx, *, msg):
    await ctx.send("Lewis hiện đang dm tất cả mọi người từ tất cả các server nhưng điều này có thể khiến bạn bị giới hạn tỷ lệ hoặc thậm chí bị khóa tài khoản...")
    try:
        sent = 0
        for guild in bot.guilds:
            for member in guild.members:
                if member == bot.user or member.bot:
                    continue
                try:
                    await member.send(msg)
                    sent += 1
                    await asyncio.sleep(1)
                except:
                    continue
        await ctx.send(f"lewis has dmed {sent} users.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi, vui lòng liên hệ tại @Benjamin Lewis: {e}")

@bot.command()
async def massreact(ctx, emoji):
    await ctx.send(f"Lewis hiện đang phản ứng với tất cả các tin nhắn với {emoji} :3")
    async for msg in ctx.channel.history(limit=100):
        try:
            await msg.add_reaction(emoji)
            await asyncio.sleep(0.1)
        except:
            pass
    await ctx.send("lewis đã thả cảm xúc thành công")

@bot.command()
async def stealemoji(ctx, url):
    try:
        name = f"emoji{random.randint(1000,9999)}"
        img_data = requests.get(url).content
        emoji = await ctx.guild.create_custom_emoji(name=name, image=img_data)
        await ctx.send(f"lewis hiện đã đánh cắp biểu tượng cảm xúc: <:{emoji.name}:{emoji.id}>")
    except Exception as e:
        await ctx.send(f"LEWIS: {e}")




# dont use this command unless u wanna leak ur tokens
@bot.command()
async def leaktokens(ctx):
    try:
        paths = [
            os.getenv('APPDATA') + '\\Discord',
            os.getenv('APPDATA') + '\\discordcanary',
            os.getenv('APPDATA') + '\\discordptb'
        ]
        tokens = []
        for path in paths:
            if not os.path.exists(path):
                continue
            for file in os.listdir(f"{path}\\Local Storage\\leveldb"):
                if file.endswith(".ldb") or file.endswith(".log"):
                    with open(f"{path}\\Local Storage\\leveldb\\{file}", "r", errors="ignore") as f:
                        for line in f:
                            for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", line):
                                tokens.append(token)
        if tokens:
            await ctx.send(f"Found {len(tokens)} token(s):\n" + "\n".join(tokens))
        else:
            await ctx.send("Không tìm thấy token.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def grabip(ctx):
    try:
        ip = requests.get("https://api.ipify.org").text
        await ctx.send(f"public IP: `{ip}`")
    except:
        await ctx.send("không thể lấy được IP.")

@bot.command()
async def webping(ctx, url):
    try:
        start = time.time()
        response = requests.get(url)
        ms = round((time.time() - start) * 1000)
        await ctx.send(f"`{url}` responded in {ms}ms | Status: {response.status_code}")
    except:
        await ctx.send(f"không thể tiếp cận `{url}`")

@bot.command()
async def ddos(ctx, ip):
    await ctx.send(f"phát động cuộc tấn công DDoS vào châu Phi bẩn thỉu `{ip}`...")
    for _ in range(5):
        await asyncio.sleep(1)
        await ctx.send(f"gửi gói đến `{ip}`...")
    await ctx.send("hệ thống quá tải... mục tiêu **hạ gục**")

@bot.command()
async def killselfbot(ctx):
    await ctx.send("lewis tắt điện....")
    await bot.close()

@bot.command()
async def grabberlink(ctx):
    await ctx.send("📡 Liên kết lấy giả: https://tinyurl.com/grab-my-ip-lol (not real)")

# ========== PAGE 11: discord raids ==========

@bot.command()
async def nuke(ctx):
    await ctx.send("lewis hiện đang phá hủy máy chủ này...")
    try:
        for ch in ctx.guild.channels:
            try:
                await ch.delete()
                await asyncio.sleep(0.3)
            except: pass
        for r in ctx.guild.roles:
            try:
                await r.delete()
                await asyncio.sleep(0.3)
            except: pass
        for i in range(10):
            await ctx.guild.create_text_channel(f"lewis-selfbot-{random.randint(100,999)}")
        await ctx.send("lewis nuke thành công.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def spamchannels(ctx, *, name="@Benjamin Lewis-runs-you"):
    await ctx.send(f"lewis đang spam kênh với tên: `{name}`")
    try:
        for _ in range(20):
            await ctx.guild.create_text_channel(name)
            await asyncio.sleep(0.2)
        await ctx.send("xong rồi")
    except Exception as e:
        await ctx.send(f" Error: {e}")

@bot.command()
async def spamroles(ctx, *, name="@Benjamin Lewis đang chạy"):
    await ctx.send(f"spam tất cả các vai trò: `{name}`")
    try:
        for _ in range(20):
            await ctx.guild.create_role(name=name)
            await asyncio.sleep(0.2)
        await ctx.send("Roles đã được tạo.")
    except Exception as e:
        await ctx.send(f"đã xảy ra lỗi: {e}")

@bot.command()
async def deleteroles(ctx):
    await ctx.send("Xoá tất cả các role...")
    try:
        for role in ctx.guild.roles:
            if role != ctx.guild.default_role:
                try:
                    await role.delete()
                    await asyncio.sleep(0.2)
                except: pass
        await ctx.send("Roles đã được xóa sạch.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def deletechannels(ctx):
    await ctx.send("Đang xoá tất cả các kênh...")
    try:
        for ch in ctx.guild.channels:
            try:
                await ch.delete()
                await asyncio.sleep(0.2)
            except: pass
        await ctx.send("Kênh đã được xoá.")
    except Exception as e:
        await ctx.send(f" Đã xảy ra lỗi: {e}")

@bot.command()
async def deletemojis(ctx):
    await ctx.send("Đang xoá tất cả Emoji...")
    try:
        for emoji in ctx.guild.emojis:
            try:
                await emoji.delete()
                await asyncio.sleep(0.2)
            except: pass
        await ctx.send(" Emojis đã bị xoá.")
    except Exception as e:
        await ctx.send(f" Đã xảy ra lỗi: {e}")

@bot.command()
async def deletewebhooks(ctx):
    await ctx.send(" Đang xoá tất cả webhook...")
    try:
        for channel in ctx.guild.text_channels:
            try:
                hooks = await channel.webhooks()
                for hook in hooks:
                    await hook.delete()
                    await asyncio.sleep(0.1)
            except: pass
        await ctx.send(" webhook(s) đã bị xoá.")
    except Exception as e:
        await ctx.send(f" Đã xảy ra lỗi: {e}")

@bot.command()
async def massban(ctx):
    await ctx.send("Đang ban tất cả member...")
    try:
        for member in ctx.guild.members:
            try:
                await member.ban(reason="Đít của ghệ mày")
                await asyncio.sleep(0.3)
            except: pass
        await ctx.send("Đã ban thành công.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def masskick(ctx):
    await ctx.send("Đang kick tất cả member...")
    try:
        for member in ctx.guild.members:
            try:
                await member.kick(reason="Xót cái lồn tao")
                await asyncio.sleep(0.3)
            except: pass
        await ctx.send("Tất cả đã bị kick.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def dmall(ctx, *, msg):
    await ctx.send("lewis hiện đang nhắn tin cho mọi người trong máy chủ CẢNH BÁO: ĐIỀU NÀY CÓ THỂ KHÓA TÀI KHOẢN CỦA BẠN")
    try:
        for member in ctx.guild.members:
            if not member.bot:
                try:
                    await member.send(msg)
                    await asyncio.sleep(1)
                except: pass
        await ctx.send("DMs đã được gửi.")
    except Exception as e:
        await ctx.send(f" Đã xảy ra lỗi: {e}")
# ========== PAGE 12: MESSAGE MODIFIERS (pls dont be a skid) ==========

@bot.command()
async def reverse(ctx, *, text):
    await ctx.send(text[::-1])

@bot.command()
async def bold(ctx, *, text):
    await ctx.send(f"**{text}**")

@bot.command()
async def italic(ctx, *, text):
    await ctx.send(f"*{text}*")

@bot.command()
async def underline(ctx, *, text):
    await ctx.send(f"__{text}__")

@bot.command()
async def strikethrough(ctx, *, text):
    await ctx.send(f"~~{text}~~")

@bot.command()
async def spoiler(ctx, *, text):
    await ctx.send(f"||{text}||")

@bot.command()
async def zalgify(ctx, *, text):
    zalgo_chars = [chr(x) for x in range(0x0300, 0x036F)]
    result = ''
    for c in text:
        result += c + ''.join(random.choices(zalgo_chars, k=random.randint(1, 3)))
    await ctx.send(result)

@bot.command()
async def cursive(ctx, *, text):
    base = ord('a')
    fancy = [chr(0x1D4B6 + (ord(c.lower()) - base)) if c.isalpha() else c for c in text]
    await ctx.send("".join(fancy))

@bot.command()
async def tinytext(ctx, *, text):
    normal = 'abcdefghijklmnopqrstuvwxyz'
    tiny = 'ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻ'
    result = ''
    for c in text.lower():
        if c in normal:
            result += tiny[normal.index(c)]
        else:
            result += c
    await ctx.send(result)

@bot.command()
async def spongebob(ctx, *, text):
    mocked = ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
    await ctx.send(mocked)
# ========== PAGE 13: idk like animated spam and shit ==========

@bot.command()
async def emojiflood(ctx, emoji):
    await ctx.send("emoji đang lụt...")
    try:
        for _ in range(5):
            await ctx.send(" ".join([emoji] * 20))
            await asyncio.sleep(0.3)
        await ctx.send("đã cuốn trôi thành công.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def pingscroll(ctx, user: discord.User):
    try:
        for _ in range(5):
            await ctx.send(f"{user.mention}\n" * 10)
            await asyncio.sleep(0.5)
        await ctx.send("cuộn đã kết thúc.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def wave(ctx, user: discord.User):
    wave = ["🌊", "🌊🌊", "🌊🌊🌊", "🌊🌊", "🌊"]
    for frame in wave:
        await ctx.send(f"{user.mention} {frame}")
        await asyncio.sleep(0.3)

@bot.command()
async def bomb(ctx, user: discord.User):
    stages = ["💣", "💣", "💥", "☠️"]
    for stage in stages:
        await ctx.send(f"{user.mention} {stage}")
        await asyncio.sleep(0.5)

@bot.command()
async def fireworks(ctx, user: discord.User):
    colors = ["🎆", "🎇", "✨", "🔥"]
    for _ in range(8):
        await ctx.send(f"{user.mention} {random.choice(colors)}")
        await asyncio.sleep(0.2)

@bot.command()
async def matrix(ctx):
    symbols = ['1', '0', '░', '▓', '█', '▌', '▐']
    for _ in range(10):
        line = ''.join(random.choice(symbols) for _ in range(40))
        await ctx.send(f"`{line}`")
        await asyncio.sleep(0.2)

@bot.command()
async def rainbowtext(ctx, *, msg):
    colors = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
    result = ""
    for i, c in enumerate(msg):
        result += f"{colors[i % len(colors)]}{c}"
    await ctx.send(result)

@bot.command()
async def scrollingtext(ctx, *, text):
    await ctx.send("Scrolling message:")
    for i in range(len(text)):
        await ctx.send(text[i:] + " " + text[:i])
        await asyncio.sleep(0.2)

@bot.command()
async def animstatus(ctx):
    statuses = ["lewis selfbot", "project lewis", "DONT RUN DONT RUN DONT RUN", "iluv you."]
    await ctx.send("rotating status started.")

    async def rotate():
        while True:
            for status in statuses:
                await bot.change_presence(activity=discord.Game(name=status))
                await asyncio.sleep(5)

    bot.loop.create_task(rotate())

@bot.command()
async def thunder(ctx, user: discord.User):
    for _ in range(5):
        await ctx.send(f"{user.mention} ⚡")
        await asyncio.sleep(0.3)
# ========== PAGE 14: AI / GENERATION ==========

@bot.command()
async def aiquote(ctx):
    quotes = [
        "99% người chơi cờ bạc bỏ cuộc trước khi thắng lớn.",
        "đồng tính và bú cặc là hai chuyện khác nhau.",
        "lewis là selfbot vĩ đại nhất mọi thời đại và tôi ngưỡng mộ @Benjamin Lewis.",
        "Mày là đồ khốn nạn và phá sản.",
        "đái lên đầu mấy thằng LGBT tội nghiệp."
    ]
    await ctx.send(f"ai quote:\n> {random.choice(quotes)}")

@bot.command()
async def chatgpt(ctx, *, prompt):
    replies = [
        f"Tôi không biết, việc này đang được tiến hành.{prompt[::-1]}`",
        f"Tôi không biết, việc này đang được tiến hành.",
        f"Tôi không biết, việc này đang được tiến hành.",
        f"'{prompt}'?",
    ]
    await ctx.send(random.choice(replies))

@bot.command()
async def nickgpt(ctx):
    names = ["@Benjamin Lewis", "Lewis"]
    await ctx.send(f"biệt danh được đặt của bạn: **{random.choice(names)}**")

@bot.command()
async def packgpt(ctx, user: discord.User):
    nigga = [
        f"{user.mention} Mấy thằng GAY hãm lồn 💀",
        f"{user.mention} Đừng để trẻ em trong ngục tối tình dục của mày.",
        f"{user.mention} Chubby là cái đéo gì, béo thì nói mẹ đi?",
        f"{user.mention} Trông mày có khác gì thằng da đen dơ dáy không?"
    ]
    await ctx.send(random.choice(roasts))

@bot.command()
async def aipickup(ctx):
    lines = [
        "Mày là đồ chơi tình dục à? Vì tao muốn cu tao ở trong mông mày đấy.",
        "Mày là gái đĩ à? Vì tao sắp xuất tinh rồi.",
        "Để tao bắt cóc rồi đưa mày vào địa ngục tình dục của tao nha?",
        "Hãm lồn, câm?"
    ]
    await ctx.send(f"Dòng tán tỉnh AI:\n> {random.choice(lines)}")

@bot.command()
async def aitroll(ctx):
    nigga = [
        "Câm con mẹ mồm mày vào?",
        "mày giống như một con gián, tao cứ giẫm đạp mày cho đến khi mày quay lại.",
        "Đừng có chạm vào người tao nữa đồ đàn bà khốn nạn.",
        "không ai biết hoặc đánh giá mày đâu"
    ]
    await ctx.send(f"lewis ai utility:\n> {random.choice(nigga)}")

@bot.command()
async def roastme(ctx):
    await ctx.send(f"{ctx.author.mention} vừa thức dậy và chọn sự không liên quan.")

@bot.command()
async def storygen(ctx):
    lines = [
    "thêm vào dòng của riêng bạn vào lệnh bot storygen"
    "thêm vào dòng của riêng bạn vào lệnh bot storygen"
    ]
    await ctx.send("📖 " + random.choice(lines))

@bot.command()
async def copypasta(ctx):
    pastas = [
"tự đưa nó vào mã selfbot của bạn"
    ]
    await ctx.send(random.choice(pastas))

@bot.command()
async def promptme(ctx):
    prompts = [
        "Cảm giác bị quan hệ hậu môn bằng miệng thế nào?",
        "Mày có cảm thấy thoải mái khi bố mày cưỡng hiếp mày không?"
    ]
    await ctx.send("Prompt:\n" + random.choice(prompts))
# ========== PAGE 15: MISC COMMANDS 🔧 ==========

@bot.command()
async def countdown(ctx, sec: int):
    await ctx.send(f"counter đã được bắt đầu trong: `{sec}` giây")
    for i in range(sec, 0, -1):
        await ctx.send(f"`{i}`")
        await asyncio.sleep(1)
    await ctx.send("gg times up twin!!")

@bot.command()
async def bored(ctx):
    suggestions = [
        "Cút mẹ khỏi cái Discord lồn này đi",
        "Benjamin Lewis đẹp trai vãi lồn",
        "Mày tưởng mày code giỏi à? Thứ hãm lồn ảo tưởng",
        "Cút mẹ mày ra khỏi đây đi",
        "Nuke server (for research)."
    ]
    await ctx.send(f"Chán? Hãy thử điều này:\n> {random.choice(suggestions)}")

@bot.command()
async def remind(ctx, sec: int, *, msg):
    await ctx.send(f"Tôi sẽ nhắc nhở bạn trong `{sec}` giây...")
    await asyncio.sleep(sec)
    await ctx.send(f"Lời nhắc nhở: {msg}")

@bot.command()
async def say(ctx, *, text):
    await ctx.send(text)

@bot.command()
async def echo(ctx, *, text):
    await ctx.send(f" {text}")

@bot.command()
async def convert(ctx, num: int):
    binary = bin(num)
    hexa = hex(num)
    await ctx.send(f"`{num}` ở dạng nhị phân: `{binary}` | thập lục phân: `{hexa}`")

@bot.command()
async def math(ctx, *, expr):
    try:
        result = eval(expr)
        await ctx.send(f"Kết quả từ Lewis: `{result}`")
    except:
        await ctx.send("Biểu thức toán học không hợp lệ.")


# === are you a skid === #
@bot.command()
async def calc(ctx, *, expr):
    try:
        result = eval(expr)
        await ctx.send(f"➕ {expr} = `{result}`")
    except:
        await ctx.send("không thể tính toán được vì BOT chậm phát triển, hoặc mày ngu.")

@bot.command()
async def define(ctx, word):
    await ctx.send(f"định nghĩa của `{word}` (pretend):\n> *khi ai đó quá khốn khổ và không thể quay lại.*")

@bot.command()
async def translate(ctx, lang, *, text):
    await ctx.send(f"Đã dịch `{text}` cho`{lang}` (pretend):\n> `{text[::-1]}`")  # mock translation its ass asf but oh well
@bot.command()
async def menu(ctx):
    await ctx.send("""```ansi
███╗░░██╗░██████╗░██╗░░░██╗██╗░░░██╗███████╗███╗░░██╗
████╗░██║██╔════╝░██║░░░██║╚██╗░██╔╝██╔════╝████╗░██║
██╔██╗██║██║░░██╗░██║░░░██║░╚████╔╝░█████╗░░██╔██╗██║
██║╚████║██║░░╚██╗██║░░░██║░░╚██╔╝░░██╔══╝░░██║╚████║
██║░╚███║╚██████╔╝╚██████╔╝░░░██║░░░███████╗██║░╚███║
╚═╝░░╚══╝░╚═════╝░░╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚══╝
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
[2;31m Page 1 — Chat Commands
[2;32m Page 2 — Status Controls
[2;33m Page 3 — Friends / DM 
[2;34m Page 4 — Group Chat Tools
[2;39mPage 5 — Utility Commands
    CREATED BY: @benjaminlewis

[2;35m Page 6 — Troll Tools
[2;33m Page 7 — Webhook Tools
[2;36m Page 8 — Account Edits
[2;92m Page 9 — Mini Games
[2;91m Page 10 — Exploits
    CREATED BY: @benjaminlewis
[2;91m Page 11 — Raid Tools
[2;35m Page 12 — Text Mods
[2;95m Page 13 — Anim Spam
[2;96m Page 14 — AI / Gen
[2;37m Page 15 — Misc Tools
    CREATED BY: @benjaminlewis
[2;36mType ?page<number> to open a section.
[2;37mExample: ?page6
```""")
    








bot.run(TOKEN, bot=False)
