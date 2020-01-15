Title: The contextmanager Decorator
Status: Draft
Date: 01-20-2020
Summary: Quick overview on usefulness of the contextmanager decorator and creating context managers from generators.

**Table of Contents**

[TOC]

# Overview



# Let's Code

## Create the Context Manager
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

## Use the Context Manager

```python
with chdir("/mydownloads/wordpress"):
    gather_paths()
```