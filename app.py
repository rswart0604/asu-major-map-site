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
    print('err is' + str(err))
    return 'must be valid url!'  # todo make this like a template or something idk


@app.route('/test', methods=['GET', 'POST'])
def get_info():
    if request.headers['data'].strip() != '':
        if 'current_map' not in session:  # we have no major map yet
            try:
                current_map = mm.MajorMap(request.headers['data'], loop)
            except Exception as e:
                return invalid_url(e)
            current_chart = mc.Chart(current_map)

        else:  # we're just adding to a major map
            try:
                current_map = mm.MajorMap(request.headers['data'], loop)
                current_chart = jsonpickle.decode(session['current_chart']).add_map(current_map)

            except Exception as e:
                return invalid_url(e)
        session['current_chart'] = jsonpickle.encode(current_chart)
        svg = current_chart.get_graph()
        svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
        return svg
    return 'reset svg'


@app.route('/move_data', methods=['GET', 'POST'])
def move_stuff():
    if 'current_chart' not in session:
        return ''
    current_map = jsonpickle.decode(session['current_chart']).get_map()
    courses_terms = current_map.get_terms_list(labels=True)
    terms = list(courses_terms.keys())
    print('terms' + str(terms))
    temp_courses = list(courses_terms.values())
    courses = []
    for x in temp_courses:
        for y in x:
            courses.append(y)
    out = '#####'.join(courses) + '-----' + '$$$$$'.join(terms)
    return out


@app.route("/move", methods=['GET', 'POST'])
def move_it():
    if 'current_chart' not in session:
        return ''
    if 'term' in request.headers and 'course' in request.headers:
        course = request.headers.get('course')
        term = request.headers.get('term')
    else:
        return 'reset svg'
    current_chart = jsonpickle.decode(session.get('current_chart'))
    my_map = current_chart.get_map()
    try:
        int(course[-1])
        new_course = course[:len(course)-2]
    except Exception:
        new_course = course
    current_chart.move_course(new_course, my_map.get_term(course), term)
    session['current_chart'] = jsonpickle.encode(current_chart)
    svg = current_chart.get_graph()
    svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
    return svg


@app.route('/remove', methods=['GET', 'POST'])
def remove():
    if 'current_chart' not in session:
        return ''
    if 'course' in request.headers:
        course = request.headers.get('course')
    else:
        return 'reset svg'
    current_chart = jsonpickle.decode(session.get('current_chart'))
    my_map = current_chart.get_map()
    term = my_map.get_term(course)
    try:
        int(course[-1])
        new_course = course[:len(course) - 2]
    except ValueError:
        new_course = course
    print(term)
    my_map.remove_course_at_term(new_course, term)
    new_chart = mc.Chart(my_map)
    session['current_chart'] = jsonpickle.encode(new_chart)
    svg = new_chart.get_graph()
    svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
    return svg



if __name__ == '__main__':
    print('gi')

    app.run(host='0.0.0.0')
