import asyncio
import sys
import threading

from proxybroker import Broker


async def show(proxies, proxy_list):
    while True:
        print('hi!')
        proxy = await proxies.get()
        if proxy is None: break
        # print('Found proxy: %s' % proxy)
        proxy_list.append(proxy)



def get_proxy(loop):
    p_list = []
    print(threading.enumerate())
    asyncio.set_event_loop(loop)
    # try:
    #     asyncio.get_event_loop()
    #     print('worked')
    # except RuntimeError as e:
    #     print(e)
    #     print('failed')
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     print(asyncio.get_event_loop())
    #     asyncio.set_event_loop_policy(None)
    #     # asyncio.set_event_loop_policy(None)
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    print(asyncio.get_event_loop())
    tasks = asyncio.gather(
        broker.find(types=['HTTP', 'HTTPS'], limit=1),
        show(proxies, p_list))

    # loop = asyncio.get_event_loop()
    print('got loop?')
    print(loop.is_running())
    loop.run_until_complete(tasks)
    print(loop.is_running())
    print(p_list)
    print('got tasks done')

    p = p_list[0].as_json()
    # print(str(p['host']) + ':' + str(p['port']))
    return str(p['host']) + ':' + str(p['port'])


    # p_list = []
    # try:
    #     loop = asyncio.get_event_loop()
    #     print('worked')
    # except RuntimeError as e:
    #     print(e)
    #     print('failed')
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     # asyncio.set_event_loop_policy(None)
    # proxies = asyncio.Queue()
    # broker = Broker(proxies)
    # tasks = asyncio.gather(
    #     broker.find(types=['HTTP', 'HTTPS'], limit=1),
    #     show(proxies, p_list)
    # )
    #
    # print('got loop?')
    # print(str(loop))
    #
    # loop.run_until_complete(tasks)
    # print(p_list)
    # print('got tasks done')
    #
    # p = p_list[0].as_json()
    # # print(str(p['host']) + ':' + str(p['port']))
    # return str(p['host']) + ':' + str(p['port'])
