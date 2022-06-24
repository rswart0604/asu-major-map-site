import shutil

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    if request.method == 'POST':
        print(request.values)
        # print(request.values[0][1][1])
        return render_template('test.html', foo='boo')
    return render_template('test.html')


@app.route('/test', methods=['GET', 'POST'])
def get_info():

    svg = open('cs.svg').read()
    if request.headers['data'] == 'a':
        svg = open('cse.svg').read()
        # svg = ''
    print(svg)
    return svg
    # return request.headers['data']


if __name__ == '__main__':
    app.run(debug=True)
