from html.parser import HTMLParser
import math
import re


class MLStripper(HTMLParser):
    """
    Class for stripping Html Tags
    """

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    #this function takes html string as input and put data in
    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def count_words(html_string):
    
    word_string = strip_tags(html_string)
    words = re.findall(r'\w+', word_string)
    count = len(words)
    return count


def get_read_time(html_string):
    count = count_words(html_string)
    read_time_min = math.ceil(count/200.0)
    return int(read_time_min)

