import asyncio
import random
import shutil
import threading
import asyncio

import major_map as mm
import map_chart as mc

from flask import Flask, render_template, request, make_response

app = Flask(__name__)

current_map = None
current_chart = None
counter = 0
loop = asyncio.get_event_loop()


@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    print(threading.enumerate())
    if request.method == 'POST':
        print(request.values)
        # print(request.values[0][1][1])
        return render_template('test.html', foo='boo')
    return render_template('test.html')


@app.route('/test', methods=['GET', 'POST'])
def get_info():
    global current_map, current_chart
    if request.headers['data'].strip() != '':
        # try:
            print(threading.enumerate())
            if current_map is None:
                print(request.headers['data'])
                try:
                    current_map = mm.MajorMap(request.headers['data'], loop)
                except ValueError:
                    return 'must be valid url!'  # todo make this like a template or something idk
                current_chart = mc.Chart(current_map)
            else:
                current_map = current_map + mm.MajorMap(request.headers['data'], loop)
            svg = current_chart.get_graph()
            svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
            return svg
    return ''

    # a = random.random()
    # resp = make_response(render_template('test.html'))
    # resp.set_cookie('your cookie', value=str(a))
    # return resp


    #
    # svg = open('cs.svg').read()
    # if request.headers['data'] == 'a':
    #     svg = open('cse.svg').read()
    #     # svg = ''
    # print(svg)
    # return svg
    # return request.headers['data']


if __name__ == '__main__':
    print('gi')
    app.run(host='0.0.0.0')
