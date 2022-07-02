import copy

from bs4 import BeautifulSoup
from urllib.request import urlopen, ProxyHandler
from proxy_finder import get_proxy
import aiohttp
import asyncio
import googlesearch


def flatten(nested_list) -> list:
    temp = []
    for x in nested_list:
        if type(x) is list:
            for y in x:
                temp.append(y)
        else:
            temp.append(x)
    return temp


def get_key_from_nested(some_dict: dict, some_value):
    for key, values in some_dict.items():
        for value in values:
            if value == some_value:
                return key


def get_longest_from_nested(some_dict: dict):
    out = 0
    for vals in some_dict.values():
        if len(vals) > out:
            out = len(vals)
    return out


class MajorMap:
    AEROSPACE = "https://degrees.apps.asu.edu/major-map/ASU00/ESAEROBSE/null/ALL/2020?init=false&nopassive=true"
    ENGLISH = "https://degrees.apps.asu.edu/major-map/ASU00/LAENGBA/null/ONLINE/2013?init=false&nopassive=true"
    CS = 'https://degrees.apps.asu.edu/major-map/ASU00/ESCSEBS/null/ALL/2021?init=false&nopassive=true'
    CSE = 'https://degrees.apps.asu.edu/major-map/ASU00/ESCSEBSE/null/ALL/2022'

    def __init__(self, major_map_url: str, loop=None):
        """Create your favorite major map

        :param major_map_url: the url of the major map
        """

        if 'http' not in major_map_url and 'www' not in major_map_url:
            if 'asu' not in major_map_url:
                major_map_url = 'asu ' + major_map_url
            if 'major map' not in major_map_url:
                major_map_url = 'major map ' + major_map_url
            major_map_url = [x for x in googlesearch.search('asu major map' + major_map_url)][0]

        # get our soup
        if loop is not None:
            try:
                proxy = {'http': get_proxy(loop)}
                ProxyHandler(proxy)
            except RuntimeError:
                pass
        else:
            proxy = {'http': get_proxy()}
            ProxyHandler(proxy)

        # print(proxy)
        print('before')

        for x in range(3):
            try:
                foo = urlopen(major_map_url, timeout=5)
                break
            except Exception as err:
                print('uh oh ' + str(err))
                if loop is not None:
                    proxy = {'http': get_proxy(loop)}
                else:
                    proxy = {'http': get_proxy()}
                ProxyHandler(proxy)
                pass
        if foo is None:
            raise ValueError()
        print('after')
        a = foo.read().decode('utf8')
        soup = BeautifulSoup(a, features='html.parser')

        # set up return arrays, etc. and get our tables we're looking at
        self.hours_term_list = []
        self.hours_terms_dict = {}
        self.terms_list = []
        self.terms_dict = {}
        self.terms_dict_urls = {}
        self.course_to_url = {}
        self.abbreviation_to_course_name = {}
        self.prereqs = {}
        tables = soup.find_all("table", class_="termTbl")

        self.name = soup.find('div', class_='left t1Div').get_text().strip()

        # print("hello!")  # sanity

        # go thru each table
        for table in tables:  # this will go through each term
            # here, get some preliminary data. the term number, the courses table, etc
            table_rows = table.find_all('tr')
            term_number = table_rows[0].td.span.get_text()  # there is one for each table
            courses_table = table_rows[1].td.table
            courses_table_rows = courses_table.find_all('tr')

            # sift through that courses list and get the specific courses and their credit hour amounts
            temp_hours_course_list = []
            temp_course_list = []
            temp_urls_course_list = []
            for course_tr in courses_table_rows:
                if course_tr.div is not None:  # if the course is a thing, get its data
                    course_text = course_tr.div.get_text()  # the course name

                    try:
                        hours = str(course_tr.find_all('td')[2].get_text()).split()[0]  # the credit hours needed
                    except Exception:
                        continue
                    if len(hours) == 0:
                        continue

                    course = str(course_text).strip().replace("  ", " ").replace("\n", "").replace("\r", "")
                    if course_tr.div.a is not None:
                        url = course_tr.div.a['href']
                    else:
                        url = '#None'
                    temp_urls_course_list.append((course, url))
                    self.course_to_url[course] = url
                    temp_hours_course_list.append((course, hours))  # combine the course and hours needed
                    temp_course_list.append(course)

            self.hours_term_list.append(
                copy.deepcopy(temp_hours_course_list))  # add this term's courses to our overall list
            self.hours_terms_dict[term_number] = temp_hours_course_list  # and dict
            self.terms_list.append(copy.deepcopy(temp_course_list))
            self.terms_dict[term_number] = temp_course_list
            self.terms_dict_urls[term_number] = temp_urls_course_list

    def get_name(self):
        return self.name

    def __str__(self):
        return self.get_name()

    def __add__(self, other):
        if len(self.get_terms_list()) != len(other.get_terms_list()):
            raise ValueError('Number of terms are different')
        self.name = self.get_name() + ' AND ' + other.get_name()
        # terms_list
        other_list = flatten(other.get_terms_list())
        # print(other_list)
        tmp_end = []
        i = 0
        for courses in self.get_terms_list():
            tmp = []
            for course in courses:
                # print(course)
                # print(course in other_list)
                if course not in other_list:
                    tmp.append(course)
            tmp_end.append(tmp + other.get_terms_list()[i])
            # print(tmp_end)
            i += 1
        self.terms_list = tmp_end
        # print(self.terms_list)
        # print(len(self.terms_list[2]))
        # print(len(set(self.terms_list[2])))

        # terms_dict
        self.terms_dict = dict(zip(self.terms_dict.keys(), self.terms_list))

        # hours_term_list
        tmp_end = []
        i = 0
        for courses in self.get_terms_list(hours=True):
            tmp = []
            for course, hour in courses:
                if course not in other_list:
                    tmp.append((course, hour))
            tmp_end.append(tmp + other.get_terms_list(hours=True)[i])
            i += 1
        self.hours_term_list = tmp_end

        # hours_terms_dict
        self.hours_term_dict = dict(zip(self.terms_dict.keys(), self.hours_term_list))

        # terms_dict_urls
        tmp_end = []
        i = 0
        for courses in self.get_terms_list(urls=True).values():
            tmp = []
            for course, url in courses:
                if course not in other_list:
                    tmp.append((course, url))
            tmp_end.append(tmp + list(other.get_terms_list(urls=True).values())[i])
            i += 1
        self.terms_dict_urls = dict(zip(self.terms_dict.keys(), tmp_end))
        l1, l2 = [], []
        for x in flatten(tmp_end):
            l1.append(x[0])
            l2.append(x[1])
        self.course_to_url = dict(zip(l1, l2))

        for key, value in other.prereqs:
            if key not in self.prereqs.keys():
                self.prereqs[key] = value

        return self

    def get_terms_list(self, hours=False, labels=False, urls=False, return_copy=True):
        """Will return a list of the courses in the map. Will be a nested list
        where each term's worth of courses are in their own list

        :param hours: if True, each course will instead be a tuple with their credit
        hours listed ie (course, # of credit hours)
        :param labels: if True, this will return a dict that has each list labeled by their term
        :return: with no args, a list of lists of each course (string), each list being a term
        """
        if hours and labels:
            out = self.hours_terms_dict  # {'term': [('course', 'hours'), ...], ...}
        elif labels:
            out = self.terms_dict  # {'term': ['course', ...], ...}
        elif hours:
            out = self.hours_term_list  # [[('course', 'hours'], ...], ...]
        elif urls:
            out = self.terms_dict_urls  # {'term': [('course', 'url'), ...], ...}
        else:
            out = self.terms_list  # [['course', ...], ...]
        if return_copy:
            return copy.deepcopy(out)
        else:
            return out

    def remove_courses(self, courses, abbreviated=True):
        if type(courses) is str:
            courses = (courses,)
        if abbreviated:
            courses = self.unabbreviate_courses(courses)
        for course in courses:
            # use the fact that terms_list ordering is the same as all the other lists
            key = ''
            for x in range(len(self.terms_list)):
                # print(self.terms_list[x])
                if course in self.terms_list[x]:
                    y = self.terms_list[x].index(course)
                    self.terms_list[x].remove(course)
                    self.hours_term_list[x].pop(y)
                    key = list(self.terms_dict.keys())[x]
                    self.hours_terms_dict.get(key).pop(y)
                    self.terms_dict.get(key).pop(y)
                    self.terms_dict_urls.get(key).pop(y)
                    break
        return

    def remove_course_at_term(self, course, term):
        term_index = list(self.terms_dict.keys()).index(term)
        course_index = self.terms_dict[term].index(course)
        self.hours_terms_dict[term].pop(course_index)
        self.terms_dict[term].pop(course_index)
        self.hours_term_list[term_index].pop(course_index)
        self.terms_dict_urls[term].pop(course_index)
        self.terms_list[term_index].pop(course_index)

    def get_sim_courses(self, maj_map: 'MajorMap'):
        list1 = self.terms_list
        list2 = maj_map.get_terms_list()
        out = [item for item in list1 if item in list2]
        return out

    def get_diff_courses(self, maj_map: 'MajorMap'):
        """Finds mutually exclusive courses
        :param maj_map: a major map that you want to find the exclusive courses of
        :return: a list of all courses in maj_map that are not in self
        """
        list1 = flatten(self.get_terms_list())
        list2 = flatten(maj_map.get_terms_list())
        out = [x for x in list2 if x not in list1]
        return out

    def get_total_courses(self, maj_map: 'MajorMap', labels=False):
        if labels:  # use stupid term labels
            dict1 = self.get_terms_list(False, True)
            dict2 = maj_map.get_terms_list(False, True)
            flat_list = flatten(self.get_terms_list())
            for term, courses in dict2.items():
                for course in courses:
                    if course not in flat_list:
                        dict1[term].append(course)
            return dict1
        else:
            list1 = flatten(self.get_terms_list())
            list2 = flatten(maj_map.get_terms_list())
            for x in list2:
                if x not in list1:
                    list1.append(x)
            return list1

    def get_total_hours(self):
        total = 0
        for courses in self.get_terms_list(True):
            for course, hour in courses:
                total += hour
        return total

    def get_hours_per_term(self):
        terms_and_hours = {}
        for term, courses in self.get_terms_list(True, True).items():
            tmp_hours = 0
            for course, hours in courses:
                try:
                    tmp_hours += int(hours)
                except ValueError:
                    tmp_hours += int(hours[0])  # if there's a range (ie 1-2 hours), just take the first one
            terms_and_hours[term] = tmp_hours
        return terms_and_hours

    def get_course_abbreviations(self):
        """this will return only the class abbreviation (ie ENG 101). Still keep as a dict
        *** if the course does not have a label, it will be omitted!!
        :return: a dict of classes and term labels without hours and only abbreviations. see below
        """
        foo = self.get_terms_list(False, True)
        out = {}
        for term, courses in foo.items():
            tmp_courses = []
            for course in courses:
                if course[0:3].isupper() and course[3] == ' ' and course[4:7].isdigit():
                    tmp_courses.append(course[0:7])
                    self.abbreviation_to_course_name[course[0:7]] = course
            out[term] = tmp_courses
        return out  # return is of form {term label: [course abbreviation, ...]}

    def find_prereqs(self, course_name: str):
        # take all of the abbreviations that we have
        # scrape and find the official prereqs text
        # add each item in abbreviations list that is in prereqs text and add to a list
        # turn that list into where it actually has the official naming
        # output that official naming list

        # print(course_name)
        try:
            r = self.prereqs[course_name]
            print('nailed it')
            return r
        except KeyError as e:
            pass

        url = self.course_to_url[course_name]
        if url is None or url[0] == '#' or len(url) < 34:
            return []

        # get some more soup!
        new_url = url.replace('courselist', 'mycourselistresults')
        # print(new_url)
        for x in range(3):
            try:
                foo = urlopen(new_url)
                break
            except Exception:
                pass
        if foo is None:
            raise Exception

        a = foo.read()
        a.decode("utf8")
        soup = BeautifulSoup(a, features='html.parser')
        tables = soup.find_all('td', class_='courseTitleLongColumnValue')

        if len(tables) > 1:
            return []
        else:
            text = tables[0].text

        out = []
        abbreviations = flatten(self.get_course_abbreviations().values())
        for abb in abbreviations:
            if abb in text:
                out.append(self.abbreviation_to_course_name[abb])
            elif abb[0:3] in text and abb[4:7] in text:  # going a lil complicated but cmon just work already
                out.append(self.abbreviation_to_course_name[abb])
        self.prereqs[course_name] = out
        # print(course_name + ":   " + str(self.prereqs[course_name]))
        return out

    async def get_async_prereq(self, course_name):
        async with aiohttp.ClientSession() as client:
            # print('course name?' + str(course_name))
            try:
                r = self.prereqs[course_name]
                print('nailed it')
                return r
            except KeyError as e:
                pass

            url = self.course_to_url[course_name]
            if url is None or url[0] == '#' or len(url) < 34:
                return []

            # get some more soup!
            new_url = url.replace('courselist', 'mycourselistresults')
            # print(new_url)
            # print('hi!')
            for x in range(3):
                try:
                    # print('got to the await?')
                    foo = await client.request('get', new_url)
                    # print('and made it to the other side')
                    break
                except Exception:
                    pass
            if foo is None:
                raise Exception

            soup = BeautifulSoup(await foo.text(), features='html.parser')
            tables = soup.find_all('td', class_='courseTitleLongColumnValue')
            # print(tables)

            if len(tables) > 1:
                return []
            else:
                try:
                    text = tables[0].text
                except Exception:
                    return []

            out = []
            abbreviations = flatten(self.get_course_abbreviations().values())
            for abb in abbreviations:
                if abb in text:
                    out.append(self.abbreviation_to_course_name[abb])
                elif abb[0:3] in text and abb[4:7] in text:  # going a lil complicated but cmon just work already
                    out.append(self.abbreviation_to_course_name[abb])
            self.prereqs[course_name] = out
            print(course_name + ":   " + str(self.prereqs[course_name]))
            return out

    async def async_find_all_prereqs(self):
        courses = flatten(self.get_terms_list())
        for i in range(len(courses)):
            courses[i] = self.get_async_prereq(courses[i])
        # print(courses)
        all_prereqs = await asyncio.gather(*courses)
        # print(all_prereqs)

    def find_all_prereqs(self):
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        asyncio.run(self.async_find_all_prereqs())
        print(self.prereqs)

    def unabbreviate_courses(self, courses):
        self.get_course_abbreviations()
        if type(courses) is str: courses = (courses,)
        out = []
        for course in courses:
            try:
                out.append(self.abbreviation_to_course_name[course])
            except KeyError:
                continue
        return out

    # uber specific for a dropdown menu yea i know
    def get_term(self, course):
        try:
            spot = int(course[-1])
        except ValueError:
            return get_key_from_nested(self.get_terms_list(labels=True), course)
        real_course = course[:len(course)-2]
        my_terms_list = self.get_terms_list(labels=True)
        flat_list = flatten(self.get_terms_list())
        count = flat_list.count(real_course)
        temp = []
        for x in range(count):
            term = get_key_from_nested(my_terms_list, real_course)
            my_terms_list.pop(term)
            temp.append(term)
        return temp[spot-1]

    def move_course(self, course, source, dest, abbreviation=True):
        if abbreviation:
            course = self.abbreviation_to_course_name[course]
        keys_list = list(self.terms_dict.keys())
        src_i = keys_list.index(source)
        dest_i = keys_list.index(dest)

        i = self.terms_list[src_i].index(course)
        self.terms_list[src_i].remove(course)
        self.terms_list[dest_i].append(course)

        tmp = self.hours_term_list[src_i][i]
        self.hours_term_list[src_i].remove(tmp)
        self.hours_term_list[dest_i].append(tmp)

        i = self.terms_dict[source].index(course)
        self.terms_dict[source].remove(course)
        self.terms_dict[dest].append(course)

        tmp = self.hours_terms_dict[source][i]
        self.hours_terms_dict[source].remove(tmp)
        self.hours_terms_dict[dest].append(tmp)

        tmp = self.terms_dict_urls[source][i]
        self.terms_dict_urls[source].remove(tmp)
        self.terms_dict_urls[dest].append(tmp)





if __name__ == '__main__':
    cs = MajorMap(MajorMap.CS)
    # cse = MajorMap(MajorMap.CSE, asyncio.get_event_loop())
    # cse.remove_courses('CSE 230: Computer Organization and Assembly Language Programming')
    # print(cse.hours_term_list[3])
    # print(cse.terms_dict.get('Term 4'))
    # cs_cse = cs + cse
    # pprint(cs.get_terms_list())
    # pprint(cs_cse.get_terms_list())
