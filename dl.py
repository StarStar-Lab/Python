""" PagerMaid module to handle sticker collection. """

import certifi
import ssl
from asyncio import sleep
from os import remove
from urllib import request
from io import BytesIO
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto
from telethon.errors.common import AlreadyInConversationError
from PIL import Image, ImageOps
from math import floor
from pagermaid import bot, redis, redis_status
from pagermaid.listener import listener
from pagermaid.utils import lang


@listener(is_plugin=False, outgoing=True, command="dl",
          description='大佬贴纸包',
          parameters="<emoji>")
async def sticker(context):
    """ Fetches images/stickers and add them to your pack. """
    pic_round = False
    if redis_status():
        if redis.get("sticker.round"):
            pic_round = True
        if len(context.parameter) == 1:
            if context.parameter[0] == "set_round":
                if pic_round:
                    redis.delete("sticker.round")
                    try:
                        await context.edit(lang('us_change_rounding_false'))
                    except:
                        pass
                else:
                    redis.set("sticker.round", "true")
                    try:
                        await context.edit(lang('us_change_rounding_true'))
                    except:
                        pass
                return
            elif "png" in context.parameter[0]:
                pic_round = False
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await context.get_reply_message()
    custom_emoji = False
    animated = False
    emoji = ""
    try:
        await context.edit("哥哥，你给我买这个棒棒糖，你女朋友不会生气吧?")
    except:
        pass
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            photo = BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split('/'):
            photo = BytesIO()
            try:
                await context.edit("哎，真好吃，哥，你尝一口！")
            except:
                pass
            await bot.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                emoji = message.media.document.attributes[1].alt
                custom_emoji = True
        elif (DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in
              message.media.document.attributes):
            photo = BytesIO()
            await bot.download_file(message.media.document, "AnimatedSticker.tgs")
            for index in range(len(message.media.document.attributes)):
                try:
                    emoji = message.media.document.attributes[index].alt
                    break
                except:
                    pass
            custom_emoji = True
            animated = True
            photo = 1
        else:
            try:
                await context.edit("哥哥!咱俩吃一个.....同一个棒棒糖，你女朋友知道了不会吃醋吧?")
            except:
                pass
            return
    else:
        try:
            await context.edit(lang('sticker_reply_not_sticker'))
        except:
            pass
        return

    if photo:
        split_strings = context.text.split()
        if not custom_emoji:
            emoji = "👀"
        pack = 1
        sticker_already = False
        if len(split_strings) == 3:
            pack = split_strings[2]
            if split_strings[1].replace("png", "") != "":
                emoji = split_strings[1].replace("png", "")
        elif len(split_strings) == 2:
            if split_strings[1].isnumeric():
                pack = int(split_strings[1])
            else:
                if split_strings[1].replace("png", "") != "":
                    emoji = split_strings[1].replace("png", "")

        pack_name = f"dalao_{pack}"
        pack_title = f"大佬 {pack}) 号贴纸包"
        command = '/newpack'
        file = BytesIO()

        if not animated:
            try:
                await context.edit("哥哥，你骑着小电动车带着我，你女朋友知道了不会揍我吧?")
            except:
                pass
            image = await resize_image(photo)
            if pic_round:
                try:
                    await context.edit(lang('us_static_rounding'))
                except:
                    pass
                image = await rounded_image(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")
        else:
            pack_name += "_animated"
            pack_title += " (animated)"
            command = '/newanimated'

        try:
            response = request.urlopen(
                request.Request(f'http://t.me/addstickers/{pack_name}'), context=ssl.create_default_context(cafile=certifi.where()))
        except UnicodeEncodeError:
            pack_name = 's' + hex(context.sender.id)[2:]
            if animated:
                pack_name = 's' + hex(context.sender.id)[2:] + '_animated'
            response = request.urlopen(
                request.Request(f'http://t.me/addstickers/{pack_name}'), context=ssl.create_default_context(cafile=certifi.where()))
        if not response.status == 200:
            try:
                await context.edit(lang('sticker_telegram_server_error'))
            except:
                pass
            return
        http_response = response.read().decode("utf8").split('\n')

        if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in \
                http_response:
            for _ in range(20): # 最多重试20次
                try:
                    async with bot.conversation('Stickers') as conversation:
                        await conversation.send_message('/addsticker')
                        await conversation.get_response()
                        await bot.send_read_acknowledge(conversation.chat_id)
                        await conversation.send_message(pack_name)
                        chat_response = await conversation.get_response()
                        while chat_response.text == "Whoa! That's probably enough stickers for one pack, give it a break. \
A pack can't have more than 120 stickers at the moment.":
                            pack += 1
                            pack_name = f"dalao_{pack}"
                            pack_title = f"大佬 {pack} 号贴纸包"
                            try:
                                await context.edit("你女朋友好可怕，不像我，只会心疼gie" + pack * "gie" + "~")
                            except:
                                pass
                            await conversation.send_message(pack_name)
                            chat_response = await conversation.get_response()
                            if chat_response.text == "Invalid pack selected.":
                                await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                                    context, file, emoji)
                                try:
                                    await context.edit(
                                        f"{lang('sticker_has_been_added')} [{lang('sticker_this')}](t.me/addstickers/{pack_name}) {lang('sticker_pack')}",
                                        parse_mode='md')
                                except:
                                    pass
                                return
                        await upload_sticker(animated, message, context, file, conversation)
                        await conversation.get_response()
                        await conversation.send_message(emoji)
                        await bot.send_read_acknowledge(conversation.chat_id)
                        await conversation.get_response()
                        await conversation.send_message('/done')
                        await conversation.get_response()
                        await bot.send_read_acknowledge(conversation.chat_id)
                        break
                except AlreadyInConversationError:
                    if not sticker_already:
                        try:
                            await context.edit(lang('sticker_another_running'))
                        except:
                            pass
                        sticker_already = True
                    else:
                        pass
                    await sleep(.5)
                except Exception:
                    raise
        else:
            try:
                await context.edit(lang('sticker_no_pack_exist_creating'))
            except:
                pass
            async with bot.conversation('Stickers') as conversation:
                await add_sticker(conversation, command, pack_title, pack_name, animated, message,
                                  context, file, emoji)

        try:
            await context.edit(
                f"{lang('sticker_has_been_added')} [{lang('sticker_this')}](t.me/addstickers/{pack_name}) {lang('sticker_pack')}",
                parse_mode='md')
        except:
            pass
        await sleep(5)
        try:
            await context.delete()
        except:
            pass


async def add_sticker(conversation, command, pack_title, pack_name, animated, message, context, file, emoji):
    await conversation.send_message(command)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message(pack_title)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await upload_sticker(animated, message, context, file, conversation)
    await conversation.get_response()
    await conversation.send_message(emoji)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message("/publish")
    if animated:
        await conversation.get_response()
        await conversation.send_message(f"<{pack_title}>")
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.send_message("/skip")
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await conversation.send_message(pack_name)
    await bot.send_read_acknowledge(conversation.chat_id)
    await conversation.get_response()
    await bot.send_read_acknowledge(conversation.chat_id)


async def upload_sticker(animated, message, context, file, conversation):
    if animated:
        try:
            await context.edit(lang('us_animated_uploading'))
        except:
            pass
        await conversation.send_file("AnimatedSticker.tgs", force_document=True)
        remove("AnimatedSticker.tgs")
    else:
        file.seek(0)
        try:
            await context.edit(lang('us_static_uploading'))
        except:
            pass
        await conversation.send_file(file, force_document=True)


async def resize_image(photo):
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)

    return image

async def rounded_image(photo):
    image = Image.open(photo)
    w = image.width
    h = image.height
    resize_size = 0
    # 比较长宽
    if w > h:
        resize_size = h
    else:
        resize_size = w
    half_size = floor(resize_size/2)

    # 获取圆角模版，切割成4个角
    tl = (0, 0, 256, 256)
    tr = (256, 0, 512, 256)
    bl = (0, 256, 256, 512)
    br = (256, 256, 512, 512)
    border = Image.open('pagermaid/static/images/rounded.png').convert('L')
    tlp = border.crop(tl)
    trp = border.crop(tr)
    blp = border.crop(bl)
    brp = border.crop(br)

    # 缩放四个圆角
    tlp = tlp.resize((half_size, half_size))
    trp = trp.resize((half_size, half_size))
    blp = blp.resize((half_size, half_size))
    brp = brp.resize((half_size, half_size))


    # 扩展四个角大小到目标图大小
    # tlp = ImageOps.expand(tlp, (0, 0, w - tlp.width, h - tlp.height))
    # trp = ImageOps.expand(trp, (w - trp.width, 0, 0, h - trp.height))
    # blp = ImageOps.expand(blp, (0, h - blp.height, w - blp.width, 0))
    # brp = ImageOps.expand(brp, (w - brp.width, h - brp.height, 0, 0))

    # 四个角合并到一张新图上
    ni = Image.new('RGB', (w, h), (0, 0, 0)).convert('L')
    ni.paste(tlp, (0, 0))
    ni.paste(trp, (w - trp.width, 0))
    ni.paste(blp, (0, h - blp.height))
    ni.paste(brp, (w - brp.width, h - brp.height))

    # 合并圆角和原图
    image.putalpha(ImageOps.invert(ni))

    return image
