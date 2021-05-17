import random
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="bing",
          description="随机获取壁纸")
async def bing(context):
    await context.edit("搜索壁纸中 . . .")
    status = False
    index = random.randint(0,7)
    json_url =  f"https://bing.biturl.top/?resolution=1920&format=json&index= `{str(index)}` &mkt=zh-CN"
    for _ in range(5):
        req = get(json_url)  
        if req.status_code == 200:
            data =json.load(req.text)
            image_url = data['url']
            break
    for _ in range (20): #最多重试20次
        website = random.randint(0,0)
        filename = "wallpaper" + str(random.random())[2:] + ".png"
        try:
            if website == 0:
                img = get(image_url)
            if img.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img.content)
                await context.edit("传壁纸中 . . .")
                await context.client.send_file(context.chat_id,filename,caption="#Wallpaper")
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
