import json
import random
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove

def get_url(num):
    json_url = f"https://www.bing.com/HPImageArchive.aspx?format=js&mkt=zh-CN&n=1&idx={str(num)}"
    req = get(json_url) 
    url = " "
    copyright = " "
    if req.status_code == 200:
        data = json.loads(req.text)
        url = data['images']['url']
        copyright = data['images']['copyright']
    return url, copyright
@listener(is_plugin=True, outgoing=True, command="bing",
          description="随机获取壁纸")    
async def bing(context):
    await context.edit("搜索壁纸中 . . .")
    status = False    
    for _ in range (20): #最多重试20次
        website = random.randint(0,0)
        num = random.randint(1,7)
        url, copyright = get_url(num)
        image_url = f"https://www.bing.com{url}"
        filename = "wallpaper" + str(random.random())[2:] + ".jpg"
        try:
            if website == 0 and image_url != " ":
                img = get(image_url)
            else: 
                await context.edit("无法访问API，呜呜呜 . . .")
            if img.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img.content)
                await context.edit("传壁纸中 . . .")
                await context.client.send_file(context.chat_id,filename,caption=(f"#bing wallpaper"
                                               "str(copyright)"))
                status = True
                break #成功了就赶紧结束啦！
        except:
            try:
                remove(filename)
            except:
                pass
            continue
    try:
        remove(filename)
    except:
        pass
    try:
        await context.delete()
    except:
        pass
    if not status:
        await context.client.send_message(context.chat_id,"出错了呜呜呜 ~ 试了好多好多次都无法访问到服务器 。")
