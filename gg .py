from magic_google import MagicGoogle
from pagermaid.listener import listener, config
from pagermaid.utils import lang
@listener(is_plugin=False, outgoing=True, command="gg",
          description=lang('google_des'),
          parameters="<query>")
async def googletest(context):
    """ Searches Google for a string. """
    PROXIES = [{
    'http': 'http://shangke121.xyz:1099',
    'https': 'http://shangke121.xyz:1099'
}]

    # Or MagicGoogle()
    mg = MagicGoogle(PROXIES)
    reply = await context.get_reply_message()
    query = context.arguments
    if query:
        pass
    elif reply:
        query = reply.text
    else:
        await context.edit(lang('arg_error'))
        return

    query = query.replace(' ', '+')
    await context.edit(lang('google_processing'))
    results = ""
    for i in mg.search(query=query, num=int(config['result_length'])):
        try:
            title = i['text'][0:30] + '...'
            link = i['url']
            results += f"\n[{title}]({link}) \n"
        except:
            await context.edit(lang('google_connection_error'))
            return
    await context.edit(f"**Google** |`{query}`| 🎙 🔍 \n"
                       f"{results}",
                       link_preview=False)
    await log(f"{lang('google_success')} `{query}`")
