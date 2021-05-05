""" Module to automate message deletion. """
from asyncio import sleep
import time
import random
from time import strftime
from telethon.tl.functions.account import UpdateProfileRequest
from emoji import emojize
from pagermaid import bot, log
from pagermaid.listener import listener

star = emojize(":star:", use_aliases=True)
star2 = emojize(":star2:", use_aliases=True)
bottle = emojize(":baby_bottle:", use_aliases=True)
ctd = '千反田が好き'
iga = '𝒶'
igh = '𝒽'
@listener(is_plugin=True, outgoing=True, command="acn",
          description="每 30 秒更新一次 last_name")
async def change_name_auto(context):
    await context.delete()
    await log("开始每 30 秒更新一次 last_name")
    while True:
        try:
            time_cur = strftime("%H:%M:%S:%p:%a", time.localtime())
            hour, minu, seco, p, abbwn = time_cur.split(':')
            if seco == '00' or seco == '30':
                for_fun = random.random()
                ahhh = random.randint(3, 7)
                first_name = iga + ahhh * igh + ' ' + '|' + ' '
                if for_fun < 0.25:
                    last_name = '%s' % (ctd)
                elif for_fun < 0.50:
                    last_name = '%s' % (star)
                elif for_fun < 0.75:
                    last_name = '%s' % (star2)
                else:
                    last_name = '%s' % (bottle)

                await bot(UpdateProfileRequest(last_name=last_name))
                await sleep(1)
                await bot(UpdateProfileRequest(first_name=first_name))
        except:
            pass
        await sleep(1)
