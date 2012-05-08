#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Data generation script, for testing purposes

import random
import datetime
import re

words = open('/usr/share/dict/american-english-large','r').read().splitlines()
re_slug = re.compile(r'[^0-9A-Za-z\-]')

def generate_phrase(wordcount):
    return " ".join([random.choice(words) for i in range(wordcount)]).capitalize()

def generate_paragraph(wordcount):
    text = []
    while wordcount > 0:
        _phrase_words = random.randint(4, 8)
        text.append("%s." % generate_phrase(_phrase_words))
        wordcount -= _phrase_words
    return " ".join(text)

def generate_date(daysback):
    return datetime.datetime.now() - datetime.timedelta(days=random.randint(0, daysback), seconds=3600*24)

def generate_email():
    return "%s %s <%s@%s.%s>" % (
        random.choice(words).capitalize(),
        random.choice(words).capitalize(),
        re_slug.sub('', random.choice(words)).lower(),
        re_slug.sub('', random.choice(words)).lower(),
        random.choice(['com','org','net','biz'])
    )

