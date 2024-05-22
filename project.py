#  RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz

#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.get('id', None)
        title = translate_html(entry.get('title', ''))
        link = entry.get('link', '')
        description = translate_html(entry.get('description', entry.get('summary', '')))
        pubdate = translate_html(entry.get('published', ''))

        # Try parsing the date with different formats
        date_formats = ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%SZ"]
        for date_format in date_formats:
            try:
                pubdate = datetime.strptime(pubdate, date_format)
                pubdate = pubdate.replace(tzinfo=pytz.timezone("GMT"))
                break
            except ValueError:
                continue

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1
# TODO: NewsStory

class NewsStory:
    def init(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate

#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger

class PhraseTrigger(Trigger):#yeh trigger ka subclass hai
    def init(self, phrase):
        self.phrase = phrase.lower()

    def is_phrase_in(self, text):
        text = text.lower()
        for char in string.punctuation:
            text = text.replace(char, ' ')  # punctuation ko space sai exchange#
        words = text.split()  # text ko individual words bana do#
        phrase_words = self.phrase.split()  # phrase jo find karna hai us ko split kardo#
        for i in range(len(words) - len(
                phrase_words) + 1):  # if lenght of sentence is same or greter than len of phase to be found#
            phrase_found = True

            # Check each word in the phrase
            for j in range(len(phrase_words)):
                if words[i + j] != phrase_words[j]:
                    # If any word does not match, the phrase is not found
                    phrase_found = False
                    break

            # If all words matched, return True
            if phrase_found:
                return True

        # If no match was found, return False
        return False

# Problem 3
# TODO: TitleTrigger

class TitleTrigger(PhraseTrigger):#eik aur subclass
    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())

# Problem 4
# TODO: DescriptionTrigger

class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.

class TimeTrigger(Trigger):
    def init(self, time_str):
        time_format = "%d %b %Y %H:%M:%S"
        est = pytz.timezone('EST')
        self.time = est.localize(datetime.strptime(time_str, time_format))

# Problem 6
# TODO: BeforeTrigger and AfterTrigger

class BeforeTrigger(TimeTrigger):
    def evaluate(self, story):
        story_pubdate = story.get_pubdate()
        if story_pubdate.tzinfo is None:
            story_pubdate = pytz.timezone('EST').localize(story_pubdate)
        return story_pubdate < self.time

class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        story_pubdate = story.get_pubdate()
        if story_pubdate.tzinfo is None:
            story_pubdate = pytz.timezone('EST').localize(story_pubdate)
        return story_pubdate > self.time

# COMPOSITE TRIGGERS

# Problem 7
# TODO: NotTrigger

class NotTrigger(Trigger):
    def init(self, trigger):
        self.trigger = trigger

    def evaluate(self, story):
        return not self.trigger.evaluate(story)

# Problem 8
# TODO: AndTrigger
# check karega ke dono triggers present hai ya nahi
class AndTrigger(Trigger):
    def init(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)

# Problem 9
# TODO: OrTrigger

class OrTrigger(Trigger):
    def init(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)

#======================
# Filtering
#======================

# Problem 10

def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.
    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    filtered_stories = []
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered_stories.append(story)
                break
    return filtered_stories

#======================
# User-Specified Triggers
#======================

# Problem 11

def read_trigger_config(filename):
    trigger_map = {
        'TITLE': TitleTrigger,
        'DESCRIPTION': DescriptionTrigger,
        'BEFORE': BeforeTrigger,
        'AFTER': AfterTrigger,
        'NOT': NotTrigger,
        'AND': AndTrigger,
        'OR': OrTrigger
    }
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    triggers = {}
    trigger_list = []

    for line in lines:
        parts = line.split(',')
        if parts[0] == 'ADD':
            for name in parts[1:]:
                trigger_list.append(triggers[name])
        else:
            trigger_name = parts[0]
            trigger_type = parts[1]
            if trigger_type in ['TITLE', 'DESCRIPTION']:
                triggers[trigger_name] = trigger_map[trigger_type](parts[2])
            elif trigger_type in ['BEFORE', 'AFTER']:
                triggers[trigger_name] = trigger_map[trigger_type](parts[2])
            elif trigger_type == 'NOT':
                triggers[trigger_name] = trigger_map[trigger_type](triggers[parts[2]])
            elif trigger_type in ['AND', 'OR']:
                triggers[trigger_name] = trigger_map[trigger_type](triggers[parts[2]], triggers[parts[3]])

    return trigger_list

SLEEPTIME = 120  # seconds -- how often we poll

def main_thread(master):
    try:
        triggerlist = read_trigger_config('triggers.txt')

        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica", 14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []

        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title() + "\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*\n", "title")
                guidShown.append(newstory.get_guid())

        while True:
            print("Polling . . .", end=' ')
            stories = process("http://news.google.com/news?output=rss")
            stories.extend(process("http://news.yahoo.com/rss/topstories"))
            stories = filter_stories(stories, triggerlist)
            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)

            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)

if name == 'main':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
