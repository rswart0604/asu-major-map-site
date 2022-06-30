import asyncio
import random
import shutil
import threading
import asyncio
import traceback
import jsonpickle

import major_map as mm
import map_chart as mc

from flask import Flask, render_template, request, make_response, session

app = Flask(__name__)
app.secret_key = 'this is a really quite super secret key, if i do say so myself'

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


def invalid_url(err):
    print('ERR')
    print(err)
    return 'must be valid url!'  # todo make this like a template or something idk


@app.route('/test', methods=['GET', 'POST'])
def get_info():
    if request.headers['data'].strip() != '':
        if 'current_map' not in session:  # we have no major map yet
            try:
                current_map = mm.MajorMap(request.headers['data'], loop)
            except Exception as e:
                invalid_url(e)
            current_chart = mc.Chart(current_map)

        else:  # we're just adding to a major map
            try:
                temp_map = mm.MajorMap(request.headers['data'], loop)
                current_chart = jsonpickle.decode(session['current_chart']).add_map(temp_map)

            except Exception as e:
                invalid_url(e)
        session['current_chart'] = jsonpickle.encode(current_chart)
        svg = current_chart.get_graph()
        svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
        return svg
    return 'reset svg'

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
