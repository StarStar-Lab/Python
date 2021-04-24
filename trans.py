import json, requests, re
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, obtain_message, attach_log
from time import sleep

@listener(is_plugin=True, outgoing=True, command="tr",
          description="通过腾讯AI开放平台将目标消息翻译成指定的语言。ps: 中文代号为zh",
          parameters="<文本/回复消息> <指定语言>")
async def tx_t(context):
    """ PagerMaid universal translator. """
    reply = await context.get_reply_message()
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
    headers = {"user-agent": USER_AGENT}
    api_lang = ['zh', 'en', 'jp', 'kr', 'fr', 'es', 'it', 'de', 'tr', 'ru', 'ru', 'pt', 'vi', 'id', 'ms', 'th']
    lang = 'en'
    if reply:
        message = reply.text
        if context.parameter:
            if re.search(r'[a-z]{2}', context.parameter[0]):
                if context.parameter[0] in api_lang:
                    lang = context.parameter[0]
                else:
                    await context.edit("指定语言未支持，默认使用英语")
        else:
            await context.edit("未指定语言，默认使用英语")
    elif context.parameter:
        message = context.parameter[0]
        try:
            tra = context.parameter[1]
            if re.search(r'[a-z]{2}', tra):
                if tra in api_lang:
                    lang = tra
                else:
                    await context.edit("指定语言未支持，默认使用英语")
        except IndexError:
            await context.edit("未指定语言，默认使用英语")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    try:
        await context.edit("正在生成翻译中 . . .")
        tx_json = json.loads(requests.get(
            "https://xtaolink.cn/git/m/t.php?lang=" + lang + '&text=' + clear_emojis(message),
            headers=headers).content.decode(
            "utf-8"))
        if not tx_json['msg'] == 'ok':
            context.edit("出错了呜呜呜 ~ 翻译出错")
            return True
        else:
            result = '文本翻译：\n' + tx_json['data']['target_text']
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 找不到目标语言，请更正配置文件中的错误。")
        return

    if len(result) > 4096:
        await context.edit("输出超出 TG 限制，正在尝试上传文件。")
        await attach_log(result, context.chat_id, "translation.txt", context.id)
        return
    await context.edit(result)
