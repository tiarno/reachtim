Title: DIY System Monitoring, Part 1: Python
Category: Python
Date: 2019-Apr-16
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with Javascript for monitoring system health.

This is an update to the original (several years old now)
[psutil and MongoDB for System Monitoring](https://reachtim.com/articles/psutil-and-mongodb-for-system-monitoring.html)

### What's changed  {: .article-title}

- updated psutil, pymongo
- changed web server from `bottle.py` to NodeJs/Express
- changed from jquery to CDN + Chart.js

The code for this article and the next two parts will become available on my
[GitHub Repo](https://github.com/tiarno/psmonitor)

The old version is the `python2` branch. The default branch (`master`) has the code
we're going over in this article. This first (python) part is there now.

### Introduction {: .article-title}

This three-part article enables you to create your own system-monitoring web page.
You'll use Python (the `psutil` package), NodeJS, and HTML+ChartJs. 

Part 2 will cover the web server, *DIY System Monitoring, Part 2: NodeJs Server*

Part 3 will cover the JS/HTML front-end, *DIY System Monitoring, Part 3: Visualization*

You'll see how you can add capabilities to suit your own monitoring app as we go. 
This is going to be a simple dashboard app that displays the disk space, memory and cpu usage
for one or more servers.  

There are certainly much more complete options like Nagios; this
little app is not in that league.  I'm writing about it because 
I use it every day and serves my purpose. As a project, it provides a good look
at writing your own apps using Python, NodeJS and plain Javascript.

There are four steps to get this going, and we'll cover the first two in
this article.

The steps:

- get each server's vital statistics every 5 minutes with a cron job.
- load the data into a MongoDB capped collection
- set up a web server route to get the data
- set up a web page with HTML + Chart.js to visualize the data


#### A Note on the Infrastucture

There's a lot you can do with a MongoDB database and a web server.
I use the two together for all kinds of things.

This project might seem to be a lot of work to just come up with a
method for monitoring some servers. But if you already have the database
and web server it's a simple and fast project to get up and running. 

I find that having these two
tools provides me with the power to come up with new ideas and implement
them quickly.


### Getting the Data  {: .article-title}

To get the data we use mostly the same code as in the earlier article. 
Here is my current version of `load_data.py`. The `pymongo` library has
changed a bit so the code reflects that, with different syntax to connect
to the Mongo database.

First, import the libraries we'll need and connect to our MongoDB server.

```python
    from datetime import datetime

    import psutil
    import pymongo
    import socket

    conn = pymongo.MongoClient()
    db = conn.myserver
```

The following function determines whether a machine is listening
on port 10000. That's a pretty specific job and the reason for it 
is that I have a subset of 
servers that expose a daemon on port 10000 and I'd like to know if 
it goes down.  We will use this information later on the web page.
The subset of servers all have names that start with `myserver`.

You could also pass in the port number if you have a
similar need but want it to be more flexible (if, say, you have multiple
services running you want to check for). Or you can leave the function
out of your code if you don't need it.

```python
    def is_up(name):
        up = False
        if name.startswith('myserver'):
            for conn in psutil.net_connections():
                if conn.laddr.port == 10000:
                    up = True
                    break
        else:
            up = None
        return up
```

The `psutil.net_connections` function returns a list of named tuples.
The `psutil` library is easy to work with. Run this code in an
interactive python session to see the `net_connections` data.

```python
    from pprint import pprint
    import psutil
    pprint(psutil.net_connections())
```

Each tuple has properties:
file descriptor, address family, type, local link address, 
remote link address, status, and process id.

In the earlier article, I had a MongoDB collection for each server I monitored.
Once the number of servers started growing, I changed up so that now I put all the 
data into the same collection, `monitor`. 

The `main` function is where we really take advantage of the power of `psutil`.
Checkout all the measurements you can request through the package:
[psutil docs](https://psutil.readthedocs.io/en/latest/)

We populate a data document, `doc`, and insert it into the MongoDB database. `monitor` collection.

```python
    def main():
        server_name = socket.gethostname()
        doc = {
            'server': server_name,
            'date' : datetime.now(),
            'cpu' : psutil.cpu_percent(interval=1),
            'disk_app' : psutil.disk_usage('/Apps').free,
            'disk_root' : psutil.disk_usage('/').free,
            'memory' : psutil.virtual_memory().free,
            'myapp': is_up(server_name)
        }
        db.monitor.insert(doc)

    if __name__ == '__main__':
        main()

```

Each data document has:

 - the server name
 - a timestamp
 - the percent CPU being used
 - the disk usage on a mounted disk (under `/Apps`)
 - the disk usage on the local drive
 - the amount of free memory
 - a boolean showing whether my app is listening on port 10000

#### CRON

So now we have the code to query a server for its load parameters.
We set up a cron job on each server we want to monitor like this:

```
    */5 * * * * /usr/bin/python3 /path/to/your/load_data.py
```

Every 5 minutes each server will check its own health using `load_data.py`
and add that data to the MongoDB collection, `monitor`.

**Note:**
If you have a bunch of servers you can put your cron jobs in a centrally-located
file and give a command for each server::

    ssh servername "crontab -r /path/to/the/cronfile"



#### Capped Collections

So we have data coming into the collection from all our servers every five minutes.
How do you keep the collection from growing too big? Make it a capped collection.
From the MongoDB docs:

> Capped collections are fixed-size collections that support
> high-throughput operations that insert and retrieve documents
> based on insertion order. Capped collections work in a way
> similar to circular buffers: once a collection fills its allocated
> space, it makes room for new documents by overwriting the oldest
> documents in the collection.


You have to specify the size you're willing to let it grow, so I needed to 
do some calcuations:

- 1 record = 250 bytes
- 12 records an hour (cronjob fires every 5 minutes)
- 3 days of data (12\*24\*3 records)
- 16 servers
- 250\*12\*24\*3\*16 = 3,456,000 (about 3.5mb)

After living with this for a while, you might want fewer days of data or a higher
frequency of measurement. Adjust the arithmetic to suit your taste.

In a `mongo` shell, cap your collection::

    db.createCollection( "monitor", { capped: true, size: 3500000 } )

With that done, we've constantly got data collecting into our MongoDB collection 
and we can just let it run now. 

Next time, you should have some data accumlated in the database that we'll use
to monitor the servers.
