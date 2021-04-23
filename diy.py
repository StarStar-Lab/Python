import random
from time import sleep
from requests import get
from pagermaid.listener import listener
import json


@listener(is_plugin=True, outgoing=True, command="diy",
          description="随机api。")
async def diy(context):
    count = random.randint(1, 20)
    sao = 'https://api.ghser.com/saohua/?type=json'
    qh = 'https://api.lovelive.tools/api/SweetNothings/?type=json'
    zn = 'https://api.lovelive.tools/api/SweetNothing/Keyword/' + str(count)
    tg = 'https://api.muxiaoguo.cn/api/tiangourj'
    ba = 'https://xiaojieapi.com/api/v1/get/security'
    gs = 'https://api.muxiaoguo.cn/api/Gushici'
    dic = {'sao': {'id': 1, 'name': '骚话', 'link': sao}, 'qh': {'id': 2, 'name': '情话', 'link': qh},
           'zn': {'id': 3, 'name': '渣男语录', 'link': zn}, 'tg': {'id': 4, 'name': '舔狗语录', 'link': tg},
           'ba': {'id': 5, 'name': '保安日记', 'link': ba}, 'gs': {'id': 6, 'name': '古诗词', 'link': gs}}
    try:
        api = context.parameter[0]
        num = dic[api]['id']
        text = "正在编" + dic[api]['name']
        result = dic[api]['link']
    except:
        await context.edit("正在掷色子 . . .")
        num = random.randint(1, 6)
        # num = int(context.parameter[0])
        for api in dic:
            if num == dic[api]['id']:
                result = dic[api]['link']
                text = "色子点数为" + str(num) + "，" + "正在编" + dic[api]['name']
    await context.edit(text)
    status = False
    for _ in range(20):  # 最多尝试20次
        req = get(result)
        if req.status_code == 200:
            data = json.loads(req.text)
            if num == 1:
                res = data['ishan']
                await context.edit(res, parse_mode='html', link_preview=False)
            elif num == 2:
                res = random.choice(data['returnObj'])
                await context.edit(res, parse_mode='html', link_preview=False)
            elif num == 3:
                res = random.choice(data['returnObj'])
                await context.edit(res, parse_mode='html', link_preview=False)
            elif num == 4:
                res = data['data']['comment']
                await context.edit(res, parse_mode='html', link_preview=False)
            elif num == 5:
                res = data['date'] + ' ' + data['week'] + ' ' + data['weather'] + '\n' + data['msg']
                await context.edit(res, parse_mode='html', link_preview=False)
            else:
                res = data['data']['Poetry'] + '\n出自 ' + '《' + data['data']['Poem_title'] + '》' + '（' + data['data']['Poet'] + '）'
                # res = data['data']['Poem_title'] + '\n' + data['data']['Poet'] + '\n' + data['data']['Poetry']
                await context.edit(res, parse_mode='html', link_preview=False)

            status = True
            break
        else:
            continue
    if not status:
        await context.edit("出错了呜呜呜 ~ 试了好多好多次都无法访问到 API 服务器 。")
        sleep(2)
        await context.delete()
