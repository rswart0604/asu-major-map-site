import asyncio
import random
import shutil
import threading
import asyncio
import traceback
import uuid

import flask
import jsonpickle

import major_map as mm
import map_chart as mc

from flask import Flask, render_template, request, make_response, session

app = Flask(__name__)
app.secret_key = 'this is a really quite super secret key, if i do say so myself'
# app.config["SESSION_TYPE"] = "filesystem"

counter = 0
loop = asyncio.get_event_loop()

chart_dict = {}


@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    return render_template('test.html')


def invalid_url(err):
    print('ERR')
    print('err is' + str(err))
    return 'must be valid url!'  # todo make this like a template or something idk


@app.route('/test', methods=['GET', 'POST'])
def get_info():
    print(request.cookies)
    if request.headers['data'].strip() != '':
        if 'key' not in request.cookies or request.cookies.get('key') not in chart_dict:  # we have no major map yet
            try:
                current_map = mm.MajorMap(request.headers['data'], loop)
            except Exception as e:
                return invalid_url(e)
            current_chart = mc.Chart(current_map)
            print('first map')
            new_key = str(uuid.uuid1())
        else:  # we're just adding to a major map
            try:
                print('hiya')
                current_map = mm.MajorMap(request.headers['data'], loop)
                new_key = request.cookies.get('key')
                current_chart = chart_dict.get(new_key)
                current_chart.add_map(current_map)
            except Exception as e:
                return invalid_url(e)
        print('the pickle is' + str(jsonpickle.encode(current_chart)))
        svg = current_chart.get_graph()
        svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
        res = make_response(svg)
        res.set_cookie('key', new_key)
        chart_dict[new_key] = current_chart
        return res
    return 'reset svg'


@app.route('/move_data', methods=['GET', 'POST'])
def move_stuff():
    if 'key' not in request.cookies:
        return ''
    current_map = chart_dict.get(request.cookies.get('key')).get_map()
    print('current map ' + str(current_map))
    courses_terms = current_map.get_terms_list(labels=True)
    print(courses_terms)
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
    if 'key' not in request.cookies:
        return ''
    if 'term' in request.headers and 'course' in request.headers:
        course = request.headers.get('course')
        term = request.headers.get('term')
    else:
        return 'reset svg'
    current_chart = chart_dict.get(request.cookies.get('key'))
    my_map = current_chart.get_map()
    try:
        int(course[-1])
        new_course = course[:len(course) - 2]
    except Exception:
        new_course = course
    current_chart.move_course(new_course, my_map.get_term(course), term)
    svg = current_chart.get_graph()
    svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
    return svg


@app.route('/remove', methods=['GET', 'POST'])
def remove():
    if 'key' not in request.cookies:
        return ''
    if 'course' in request.headers:
        course = request.headers.get('course')
    else:
        return 'reset svg'
    current_chart = chart_dict.get(request.cookies.get('key'))
    my_map = current_chart.get_map()
    term = my_map.get_term(course)
    try:
        int(course[-1])
        new_course = course[:len(course) - 2]
    except ValueError:
        new_course = course
    print(term)
    current_chart.remove_course(new_course, term)

    svg = current_chart.get_graph()
    svg = svg[:5] + 'id="major_map_svg" ' + svg[5:]
    res = flask.make_response(svg)
    return res


@app.route('/delete_cookie', methods=['GET', 'POST'])
def del_cookie():
    print('outta here')
    the_key = request.cookies.get('key')
    chart_dict.pop(the_key)
    res = make_response('')
    res.set_cookie('key', 'null')
    return res


if __name__ == '__main__':
    print('gi')

    app.run(host='0.0.0.0')
