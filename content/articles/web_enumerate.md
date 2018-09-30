Title: Enumerate Web from Framework
Status: Draft
Date: 10-20-2018
Tags: Python, Security
Category: Security
Summary: Enumerate a Web Framework with Python.

**Table of Contents**

[TOC]

# Overview {: .article-title}

stuff

# Download WordPress ##

https://wordpress.org/latest.tar.gz


- Target website uses a popular framework.
- enumerate that website for further attacks.


# `enumeration with mapper.py` 

<span style="color:lightblue">Demo</script>


```python
def get_words(wordlist, resume=None):
    with open(wordlist) as f:
        raw_words = f.read()
    found_resume = False
    words = list()
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                words.append(word)
            else:
                if word == resume:
                    found_resume = True
                    print(f'Resuming wordlist from: {resume}')
        else:
            words.append(word)
    return words
```


```python
import contextlib
import os
import queue
import requests
import sys
import threading
import time

FILTERS = [".jpg", ".gif", ".png", ".css"]
TARGET = "http://example.com/wordpress"
THREADS = 10

web_paths = queue.Queue()
answers = queue.Queue()

@contextlib.contextmanager
def chdir(path):
    """
    On enter, change directory to specified path.
    On exit, change directory to original.
    """
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(this_dir)


def gather_paths():
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILTERS:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)

def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = f'{TARGET}{path}'
        time.sleep(2)
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            
def run():
    mythreads = list()
    for i in range(THREADS):
        print(f'Spawning thread {i}')
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()

    for thread in mythreads:
        thread.join()
        

if __name__ == '__main__':
    with chdir("/mydownloads/wordpress"):
        gather_paths()
    run()
    with open('myanswers.txt', 'w') as f:
        for answer in list(answers.queue):
            f.write(f'{answer}\n')
    print('done')

```

# HTTP Status Codes

https://www.restapitutorial.com/httpstatuscodes.html
