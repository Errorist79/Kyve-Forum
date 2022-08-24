import requests
import os
import json
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
import discord
import info


### Değişkenler ###
TOKEN = info.TOKEN
CHANNEL_ID = info.CHANNEL_ID
query_time = info.query_time


Bot = commands.Bot("$")
## Bot bağlantısı ##
@Bot.event
async def on_ready():
    check_control_data.start()

## Sürekli sorguyu çalıştırma ##
@tasks.loop(seconds=query_time)
async def check_control_data():
    con = requests.get("https://forum.kyve.network/latest.json").json()["topic_list"]["topics"]
    img_data = requests.get("https://forum.kyve.network/latest.json").json()["users"]
    file_json = "data.json"
    for information in con:
        try:
            option = 0
            for old_data in json.load(open(file_json, "r", encoding="utf-8")):
                if old_data["id"] == information["id"]:
                    option = 1
                    break
            if option == 1:
                continue
        except:
            pass
                
        a = []
        if not os.path.isfile(file_json):
            a.append(information)
            with open(file_json, mode='w', encoding="utf-8") as f:
                f.write(json.dumps(a, indent=2,ensure_ascii=False))
        else:
            with open(file_json, encoding="utf-8") as feedsjson:
                feeds = json.load(feedsjson)

            feeds.append(information)
            with open(file_json, mode='w', encoding="utf-8") as f:
                f.write(json.dumps(feeds, indent=2,ensure_ascii=False))
        

        link = "https://forum.kyve.network/t/" + information["slug"] + "/"
        title = information["title"]
        html_content = requests.get(link)
        soup = BeautifulSoup(html_content.text, 'html.parser')

        text_content = soup.get_text(strip=True,separator=",,,")
        text_content_split = text_content.split(",,,")

        i = 0
        for bas in text_content_split:
            try:
                int(bas.split(",")[0].split(" ")[1])
                break
            except:
                pass

            i+=1
        
        author = text_content_split[i-1]

        i = 0
        a = 0
        for bas in text_content_split:
            try:
                if bas == "#1":
                    a = i
                if bas.split(" ")[-1] == "Likes" or bas.split(" ")[-1] == "Like":
                    break
            except:
                pass

            i+=1

        description = ' '.join(str(x) for x in text_content_split[a+1:i]).replace(",,,", " ").replace(",Home,Categories,FAQ/Guidelines,Terms of Service,Privacy Policy,Powered by,Discourse,, best viewed with JavaScript enabled"," ").replace(".,",".\n").replace(",:",":").replace("Home Categories FAQ/Guidelines Terms of Service Privacy Policy Powered by Discourse , best viewed with JavaScript enabled", " ")
        
        category = text_content_split[0].split(" - ")[1]
        if category == "Announcement":
            continue
        
        for img_d in img_data:
            if img_d["username"] == author:
                
                if img_d["avatar_template"].split("/")[0] == "https:":
                    img_link = img_d["avatar_template"].replace("{size}", "32")
                else:
                    img_link = "https://dub2.discourse-cdn.com/standard20" + img_d["avatar_template"].replace("{size}", "32")
                    
                break

        embed = discord.Embed()
        embed.color = 0xFF0000
        embed.add_field(name="Category", value=category, inline=False)
        embed.set_author(name=author, icon_url=img_link)
        embed.title = title
        embed.description = description
        embed.url = link
        await Bot.get_channel(CHANNEL_ID).send(embed=embed)

Bot.run(TOKEN)