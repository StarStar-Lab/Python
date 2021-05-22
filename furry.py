import random  
from time import sleep
from requests import get
from pagermaid.listener import listener
from os import remove


@listener(is_plugin=True, outgoing=True, command="furry",
          description="随机获取furry图")
async def ghs(context):
    await context.edit("搞颜色中 . . .")
    status = False
    for _ in range (20): #最多重试20次
        filename = "furry" + str(random.random())[2:] + ".png"
        try:
            img = get("https://api.furryowo.top/api/tupian/index.php")
            if img.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(img.content)
                await context.edit("传颜色中 . . .")
                await context.client.send_file(context.chat_id,filename,caption="#Furry")
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
        await context.client.send_message(context.chat_id,"出错了呜呜呜 ~ 试了好多好多次都无法访问到服务器（没有furry看啦！） 。")
