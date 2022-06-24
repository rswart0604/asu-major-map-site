import asyncio
from proxybroker import Broker


async def show(proxies, proxy_list):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        # print('Found proxy: %s' % proxy)
        proxy_list.append(proxy)


def get_proxy():
    p_list = []
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(
        broker.find(types=['HTTP', 'HTTPS'], limit=1),
        show(proxies, p_list))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)

    p = p_list[0].as_json()
    # print(str(p['host']) + ':' + str(p['port']))
    return str(p['host']) + ':' + str(p['port'])
