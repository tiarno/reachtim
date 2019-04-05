Title: DIY System Monitoring, Part 1
Category: Python
Status: Draft
Date: 2019-Apr-13
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with Javascript for monitoring system health.

This is an update to the original (several years old now)
[psutil and MongoDB for System Monitoring](https://reachtim.com/articles/psutil-and-mongodb-for-system-monitoring.html)

### What's changed  {: .article-title}

- updated for psutil on Python 3.6
- changed web server from `bottle` to NodeJs/Express
- changed from jquery to CDN + Chart.js

Part 2 is here: [DIY System Monitoring, Part 2](https://reachtim.com/articles/diy-system-monitoring-part-2.html)

Part 3 is here: [DIY System Monitoring, Part 3](https://reachtim.com/articles/diy-system-monitoring-part-3.html)


There's a lot you can do with a MongoDB database and a web server 
to interact with it. I use the two together for all kinds of things.
This project might seem to be a lot of work to just come up with a
method for monitoring some servers. But if you already have the database
and web server it's simple and fast. I find that having these two
tools provides me with the power to come up with new ideas and implement
them quickly.

So, if you want to monitor some servers, this is an easy and cheap way to do it.
There are heavier frameworks and applications that will do a lot more if you need that.
I only want to check on a cluster of servers a few times a day to make sure they
aren't running out memory, diskspace, etc. 

There are four steps to get this going, and we'll cover the first two in
this article.

The steps:

- get each server's vital statistics every 5 minutes with a cron job.
- load the data into a MongoDB capped collection
- set up a web server route to get the data
- set up a web page with HTML + Chart.js to visualize the data


#### Note: 

The code for this article and the next two parts are available now on
[GitHub](https://github.com/tiarno/psmonitor)

The old version is the `python2` branch. The default branch (`master`) has the code
we're going over in this article.

### Getting the Data  {: .article-title}

To get the data we use mostly the same code as in the earlier article. 
Here is my current version of `psmonitor_data.py`. The `pymongo` library has
changed a bit so the code reflects that, with different syntax to connect
to the Mongo database.

```python
    from datetime import datetime
    import psutil
    import pymongo
    import socket

    conn = pymongo.MongoClient(host='myserver', replicaSet='rs1')
    db = conn.myserver
```

In this version,
I also added a function to find out if a machine is listening
on port 10000. I have a subset of servers that expose a daemon
on port 10000 and I'd like to know if it goes down. 

We will use this information later on the web page.

```python
    def is_up(name):
        up = 'false'
        if name.startswith('myserver'):
            for conn in psutil.net_connections():
                if conn.laddr.port == 10000:
                    up = 'true'
                    break
        else:
            up = 'NA'
        return up

```

One other change is that instead of having a different MongoDB collection for 
each server, I put all the data into the same collection and I called it
`monitor`. This is how that looks in python:

```python
    doc = dict()
    doc['server'] = socket.gethostname()
    doc['date'] = datetime.now()
    doc['amd'] = get_cpu('amd')
    doc['disk_app'] = disk_app.free
    doc['disk_root'] = disk_root.free
    doc['phymem'] = phymem.free

    doc['cpu'] = {'user': cpu.user, 'nice': cpu.nice,
                'system': cpu.system, 'idle': cpu.idle,
                'irq': cpu.irq}

    doc['myserverUp'] = is_up(doc['server'])
    db.monitor.insert(doc)
```

So now we have the code to query a server for its load parameters.
We set up a cron job on each server we want to monitor like this:

```
    */5 * * * * /usr/bin/python3 /path/to/your/psmonitor_data.py
```

Every 5 minutes each server will check its own health using `psmonitor_data.py`
and add that data to the MongoDB collection, `monitor`.

#### Capped Collections

How do you keep the collection from growing too big? Make it a capped collection.
You have to specify the size you're willing to let it grow, so I needed to 
do some calcuations::

- 1 record = 250 bytes
- 12 records an hour (cronjob fires every 5 minutes)
- 3 days of data (12\*24\*3 records)
- 16 servers
- 250\*12\*24\*3\*16 = 3,456,000 (about 3.5mb)

In a `mongo` shell, cap your collection::

    db.createCollection( "monitor", { capped: true, size: 3500000 } )

The rest of the code is the same. 

With that done, we've constantly got data collecting into our MongoDB collection 
and we can just let it run now. 

Next time, you should have some data accumlated in the database that we'll use
to monitor the servers.



