import copy
import random
import time

import major_map
from major_map import MajorMap
import schemdraw
from schemdraw import flow
import math
from pprint import pprint


def format_words(course: str):
    words = course.split()
    word_list = []
    tmp = ""
    for word in words:
        tmp += (word + " ")
        if len(tmp) > 12:
            word_list.append((tmp + '\n'))

            tmp = str('')
    if tmp != '':
        word_list.append(tmp)
    result = ''.join(word_list)
    if result == '':  # if we only have one word for our course (ie 'Elective'), this catches that
        result = course
    result = result.replace('&', 'and')
    return result


class Chart:

    def __init__(self, *args):
        """We want this class to be able to handle not just MajorMap objects, but possibly lists
        made by combining major map term lists, etc
        :param args: a MajorMap object, a dict from a MajorMap, or a nested list of courses in a map
        """
        if type(args[0]) is MajorMap:
            self.map = args[0].get_terms_list(False, True, return_copy=False)
            self.maj_map = args[0]
        else:
            self.map = args[0]
            self.maj_map = None
        self.BOX_WIDTH = 5
        self.BOX_HEIGHT = 4
        self.dx = 2
        self.dy = 2
        self.removed_courses = []
        self.wires_colors = {}

    def get_graph(self):
        file_name = str(self.maj_map).lower().replace(' ', '_') \
                    + '.svg' if self.maj_map is not None else 'major_map.svg'
        with schemdraw.Drawing(file=file_name, fontsize=12) as d:

            if self.maj_map is not None:
                print('MAJ MAP!!!')

                flat_list = major_map.flatten(self.maj_map.get_terms_list())
                prereq_to_n = dict(zip(flat_list, [0] * len(flat_list)))
                course_to_n = copy.deepcopy(prereq_to_n)

                y_channels = [0] * (len(self.map) - 1)
                max_courses = major_map.get_longest_from_nested(self.maj_map.get_terms_list(labels=True))
                if max_courses > 5:
                    self.dy = 2.4
                    self.dx = 2.6
                x_channels = [0] * max_courses

                course_to_box = {}
                x_pos = 0

                for term, courses in self.map.items():
                    d += flow.Box(w=self.BOX_WIDTH, h=self.BOX_HEIGHT).label(term).at((x_pos, 0))  # our term label
                    y_pos = 0
                    for course in courses:  # go through each term's courses pls
                        y_pos -= (self.BOX_HEIGHT + self.dy)

                        # stupid stupid string formatting stuff. no more than 20 chars per line allowed
                        result = format_words(course)

                        course_to_box[course] = flow.Box(w=self.BOX_WIDTH, h=self.BOX_HEIGHT).label(result).at(
                            (x_pos, y_pos))
                        d += course_to_box[course]
                        prereqs = self.maj_map.find_prereqs(course)
                        if len(prereqs) > 0 and x_pos > 0:
                            # print(course + ": " + str(prereqs))
                            for prereq in set(prereqs):
                                if prereq != course:

                                    try:
                                        p_x, p_y = course_to_box[prereq].E[0], course_to_box[prereq].E[1]
                                    except KeyError:
                                        continue
                                    c_x, c_y = course_to_box[course].W[0], course_to_box[course].W[1]

                                    if math.isclose(p_y,
                                                    c_y) and c_x - p_x < self.dx + .1:  # we're right next to each other, with same y
                                        d += flow.Arc2(arrow='->', k=.3).at((p_x, p_y)).to((c_x, c_y))
                                    elif math.isclose(c_x - p_x, self.dx):  # we're right next to each other but diff y
                                        try:
                                            color = self.wires_colors[(prereq, course)]
                                        except KeyError:
                                            color = random.choice(colors)[1]
                                            self.wires_colors[(prereq, course)] = color
                                        d += flow.ArcZ(arrow='->').at((p_x, p_y)).to((c_x, c_y)).color(color)
                                    else:  # far away in terms of x
                                        pre_term_rev = major_map.get_key_from_nested(
                                            self.maj_map.get_terms_list(labels=True),
                                            prereq)[::-1]
                                        for char in pre_term_rev:
                                            if char.isdigit():
                                                y_ind = int(char) - 2
                                                y_channels[y_ind] = y_channels[y_ind] + 1
                                        x_ind = self.map[term].index(course)
                                        x_channels[x_ind] = x_channels[x_ind] + 1

                                        tmp_point = (p_x + .2 * y_channels[y_ind], c_y + 2 + (
                                                    .2 * x_channels[x_ind]))
                                        try:
                                            color = self.wires_colors[(prereq, course)]
                                        except KeyError:
                                            color = random.choice(colors)[1]
                                            self.wires_colors[(prereq, course)] = color
                                        d += flow.Wire(shape='c', k=.2 * y_channels[y_ind]).at((p_x, p_y + .4 - (.2 * prereq_to_n[prereq]))).to(tmp_point).color(color)
                                        d += flow.Wire(shape='c', k=(c_x - tmp_point[0] - .3), arrow='->').at(
                                            tmp_point).to((c_x, c_y + .6 - .2 * course_to_n[course])).color(color)
                                        prereq_to_n[prereq] = prereq_to_n[prereq] + 1
                                        course_to_n[course] = course_to_n[course] + 1

                    x_pos += (self.BOX_WIDTH + self.dx)
            elif type(self.map) is dict:  # term labels! yay! for once!
                x_pos = 0
                for term, courses in self.map.items():
                    d += flow.Box(w=self.BOX_WIDTH, h=self.BOX_HEIGHT).label(term).at((x_pos, 0))  # our term label
                    y_pos = 0
                    for course in courses:  # go through each term's courses pls
                        y_pos -= (self.BOX_HEIGHT + self.dy)

                        result = format_words(course)

                        d += flow.Box(w=self.BOX_WIDTH, h=self.BOX_HEIGHT).label(result.strip()).at((x_pos, y_pos))
                    x_pos += (self.BOX_WIDTH + self.dx)
            else:  # we got a nested list on our hands
                x_pos = 0
                for courses in self.map:
                    y_pos = self.BOX_HEIGHT + self.dy
                    for course in courses:
                        y_pos -= (self.BOX_HEIGHT + self.dy)

                        result = format_words(course)

                        d += flow.Box(w=self.BOX_WIDTH, h=self.BOX_HEIGHT).label(result).at((x_pos, y_pos))
                    x_pos += (self.BOX_WIDTH + self.dx)




colors = [
    ["aqua marine", "#7FFFD4"],
    ["bisque", "#FFE4C4"],
    ["Black", "#000000"],
    ["black", "#000000"],
    ["Blue", "#0000FF"],
    ["blue", "#0000FF"],
    ["blue violet", "#8A2BE2"],
    ["brown", "#A52A2A"],
    ["burly wood", "#DEB887"],
    ["cadet blue", "#5F9EA0"],
    ["chocolate", "#D2691E"],
    ["coral", "#FF7F50"],
    ["corn flower blue", "#6495ED"],
    ["crimson", "#DC143C"],
    ["dark blue", "#00008B"],
    ["dark cyan", "#008B8B"],
    ["dark golden rod", "#B8860B"],
    ["dark gray", "#A9A9A9"],
    ["dark green", "#006400"],
    ["dark khaki", "#BDB76B"],
    ["dark magenta", "#8B008B"],
    ["dark olive green", "#556B2F"],
    ["dark orange", "#FF8C00"],
    ["dark orchid", "#9932CC"],
    ["dark red", "#8B0000"],
    ["dark red", "#8B0000"],
    ["dark salmon", "#E9967A"],
    ["dark sea green", "#8FBC8F"],
    ["dark slate blue", "#483D8B"],
    ["dark slate gray", "#2F4F4F"],
    ["dark turquoise", "#00CED1"],
    ["dark violet", "#9400D3"],
    ["deep pink", "#FF1493"],
    ["deep sky blue", "#00BFFF"],
    ["dim gray-dim grey", "#696969"],
    ["dodger blue", "#1E90FF"],
    ["firebrick", "#B22222"],
    ["forest green", "#228B22"],
    ["gold", "#FFD700"],
    ["golden rod", "#DAA520"],
    ["Gray", "#808080"],
    ["gray-grey", "#808080"],
    ["Green", "#008000"],
    ["green", "#008000"],
    ["green yellow", "#ADFF2F"],
    ["hot pink", "#FF69B4"],
    ["indian red", "#CD5C5C"],
    ["indigo", "#4B0082"],
    ["khaki", "#F0E68C"],
    ["light coral", "#F08080"],
    ["light green", "#90EE90"],
    ["light pink", "#FFB6C1"],
    ["light salmon", "#FFA07A"],
    ["light sea green", "#20B2AA"],
    ["light sky blue", "#87CEFA"],
    ["light slate gray", "#778899"],
    ["light steel blue", "#B0C4DE"],
    ["Lime", "#00FF00"],
    ["lime", "#00FF00"],
    ["lime green", "#32CD32"],
    ["Maroon", "#800000"],
    ["maroon", "#800000"],
    ["medium aqua marine", "#66CDAA"],
    ["medium blue", "#0000CD"],
    ["medium orchid", "#BA55D3"],
    ["medium purple", "#9370DB"],
    ["medium sea green", "#3CB371"],
    ["medium slate blue", "#7B68EE"],
    ["medium spring green", "#00FA9A"],
    ["medium turquoise", "#48D1CC"],
    ["medium violet red", "#C71585"],
    ["midnight blue", "#191970"],
    ["navajo white", "#FFDEAD"],
    ["navy", "#000080"],
    ["Olive", "#808000"],
    ["olive", "#808000"],
    ["olive drab", "#6B8E23"],
    ["orange", "#FFA500"],
    ["orange red", "#FF4500"],
    ["orchid", "#DA70D6"],
    ["pale golden rod", "#EEE8AA"],
    ["pale green", "#98FB98"],
    ["pale turquoise", "#AFEEEE"],
    ["pale violet red", "#DB7093"],
    ["peru", "#CD853F"],
    ["plum", "#DDA0DD"],
    ["powder blue", "#B0E0E6"],
    ["Purple", "#800080"],
    ["purple", "#800080"],
    ["Red", "#FF0000"],
    ["red", "#FF0000"],
    ["rosy brown", "#BC8F8F"],
    ["royal blue", "#4169E1"],
    ["saddle brown", "#8B4513"],
    ["salmon", "#FA8072"],
    ["sandy brown", "#F4A460"],
    ["sea green", "#2E8B57"],
    ["sienna", "#A0522D"],
    ["sky blue", "#87CEEB"],
    ["slate blue", "#6A5ACD"],
    ["slate gray", "#708090"],
    ["spring green", "#00FF7F"],
    ["steel blue", "#4682B4"],
    ["tan", "#D2B48C"],
    ["Teal", "#008080"],
    ["teal", "#008080"],
    ["thistle", "#D8BFD8"],
    ["tomato", "#FF6347"],
    ["turquoise", "#40E0D0"],
    ["violet", "#EE82EE"],
    ["yellow", "#FFFF00"],
    ["yellow green", "#9ACD32"]
]


if __name__ == '__main__':
    start = time.time()
    cs = MajorMap(MajorMap.CS)
    c = Chart(cs)
    c.get_graph()
    cs.move_course('CSE 110', 'Term 1', 'Term 2')
    # print(cs.get_terms_list(False, True))
    c.get_graph()
    print(time.time() - start)
