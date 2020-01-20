Title: The contextmanager Decorator
Tags: Python, hacking
Category: Python
Status: Draft
Date: 01-22-2020
Summary: Quick overview on usefulness of the contextmanager decorator and creating context managers from generators.

**Table of Contents**

[TOC]

# Overview

> Generally, you create a context manager by creating a class with `__enter__` and `__exit__` methods, but this example shows you how to use the `@contextlib.contextmanager` to create a simple context manager.

Context managers provide a cool programming pattern, especially if you're forgetful or 
just have too much to keep track of and you want to simplify your life.

You'll find them helpful when you have opened something and need to close it, locked something and need to release
it, or changed something and need to reset it.  There are several built in context managers that you're probably
familiar with like `open` to open a file or `socket` to use a socket.  The bog-standard example:

```python
with open('myfile.txt') as f:
    lines = f.readlines()

do_stuff(lines)
```

The `open` context manager opens a file, returns an object we name as `f`. When we've done all the
things we're going to with it,
(we fall out of the `with` statement block), the file is automatically closed for us.

In this brief article, you'll see how you can create a dead-simple context manager from a generator.


# Let's Code

## Create the Context Manager

First import the `contextlib` module. It has several helpers 
(read more here: [contextlib module](https://docs.python.org/3/library/contextlib.html)).

We're just going to decorate the `chdir` function as a `contextlib.contextmanager`.

```python
import contextlib

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
```

To make this work, the function must be a generator and `yield` exactly once.
At the point of the `yield`, the calling process is executed.

In `chdir`, the function takes a single argument, `path`. 

1. First it makes a note of the current directory and then changes to the `path`.
2. Then it yields control back to the caller.
3. No matter what happens during that process, the function will `finally` change back to the original directory.

## Use the Context Manager

Suppose you have some function `gather_paths` you want to call for a set of directories.
The following example shows how the `chdir` context manager could be used:

```python
with chdir("/mydownloads/wordpress"):
    gather_paths()
```

I like this little context manager; it keeps me from having to remember to switch back
to the original directory so I don't get surprised later and find my program is executing
somewhere else.

As long as I call the function as a context manager using the `with` statement,
I don't have to remember to change back to the original directory or do anything special.
