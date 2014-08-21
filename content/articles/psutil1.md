Title: psutil and MongoDB for Monitoring
Category: Python
Status: Draft
Date: 2014-Aug-24
Tags: sysadmin, python, web
Summary: How to use psutil and MongoDB for monitoring system health.

This article shows how to create a set of charts for monitoring one or more machines. It uses Python (psutil and bottle), MongoDb, and jquery. The general idea is the same no matter if you use a different database or web framework.

At the end of the process, you will have a web page for each machine that displays charts showing cpu, memory, and disk usage.

[TOC]

I need to watch a couple of FreeBSD machines to make sure they're healthy and not running into memory or disk space issues. Their names are `example01` and `example02`.

I don't want to go to each machine and run `top` or `ds` to find out what's going on, I want a web page with up-to-date charts that I can glance at, one page per machine.

The overall workflow follows these three steps:

1. Get the system data into MongoDB (`psutil` and `cron`).
2. Write a short HTML page to display the data (`jqplot` + AJAX).
3. Set up a web server to query the MongoDB server (`bottle`).

You can get all the code in my GitHub project [psmonitor](https://github.com/tiarno/psmonitor). I use snippets of that code in this article.

In the first part, I use the `psutil` package inside a `cron` job to write system information to a capped collection in MongoDB every 5 minutes.

In the second part, I have an HTML file corresponding to each machine. The file loads `jqplot` from jquery, and makes an AJAX request to the MongoDB collection via `bottle`.

In the third part, the `bottle` application ties it together by making the request to MongoDB and passing that data back to the HTML page.

This is an example of one of the charts we will create:
![monitor01][monitor01]

You can make charts for any data you want. 
The charts I use for each machine are:

* cpu user percent
* cpu system percent
* cpu irq
* cpu nice percent
* disk space free
* memory free
    
### Part 0: Get the Tools {: .article-title}

The following tools are the ones to install for this implementation, but you can use a different database or web framework if you already have one.

The `psutil` Python package is a great cross-platform tool for system monitoring. Read more about it on its [project page](http://pythonhosted.org/psutil/). You can install it with `pip`.

The NOSQL database [mongoDB](http://www.mongodb.org/) is an open-source document database. If you have data that naturally fits a JSON-style structure, mongoDB is a great fit for data storage. It has become a natural tool for me anytime I find I need a JSON store.

The `bottle` web [framework](http://bottlepy.org/docs/dev/index.html) is a tiny framework written in Python with no other dependencies. You can install it with `pip`. You can use the included development server to get things going and put it under a different backend server later. I put mine under my Apache server once I got things like I wanted them.

The [jqplot](http://www.jqplot.com/) `jquery` plugin makes producing the charts easy, plus they look good and they are all uniform so it easy to compare charts. For example, it is easy to see when a process spins up because you can see the spike for cpu and memory at the same moment, which is the same x-axis location for both charts. There is a lot more you can do with this plugin, this exercise just scratches the surface.

### Part 1: Get the Data {: .article-title}

We want to create data structure that follows this pattern. The main thing is to create time series so getting the timestamp to along with the data is the point here. You can add or remove any data that psutil supports in this step. 

As my first step I wasn't sure of what I needed and would use and so this is what I started out with. I figured that as time went by and I saw the actual needs of the machine this would change, and could be easily changed.

```python
{
  datetime: datetime.now(),
  cpu:       {user:, nice:, system:, idle:, irq:,},
  disk_root: {total:, used:, free: },
  phymem:    {total:, used:, free: },
  virtmem:   {total:, used:, free: },
}
```

Here is the python code for getting data from the system (using `psutil`) into the MongoDb database. I created a collection in MongoDb for each machine to be monitored. You could create a single document in MongoDb that contains data for each machine; it depends on your needs. I didn't want a request over the network bringing in data I didn't need so I separated the collections by machine.

## About the MongoDB Collection.

I have a three-member replicaset for MongoDb, and that is not necessary but it is recommended to have a replicaset for production. The machines that hold the data happen to be the same ones I am monitoring, `example01` and `example02`.
The third member is just an arbiter and doesn't keep the data. These mongoDB server machines don't have to be the ones that are monitored, they could be anywhere.

Now for the collection that will contain the data for a single machine:
With 1440 minutes per day, sampling every 5 minutes, and keeping two days worth of data, we'll need 576 records (documents)

    (1440/5)*2 = 576 records per server 

I wasn't sure how much data I would eventually use, so I estimated 2k per document. I estimated a generous size for the documents because this is just a start and I may want to gather more data later on. Turns out that 2k is extremely generous.

    576 documents @ 2048 bytes per doc = 1,179,648 bytes

So I created a capped collection for each machine with a maximum size of 1179648 and a maximum number of 576 documents:

    db.createCollection('example01', {capped:true, size:1179648, max:576})
    db.createCollection('example02', {capped:true, size:1179648, max:576})

 By using a capped collection, we are guaranteed that the data will be preserved in insertion order, and old documents are automatically removed as time goes by so we always have the latest 48 hours of data.

First, do the necessary imports and make the connection to the MongoDb instance.

```python
#!/usr/bin/env python
from datetime import datetime
import psutil
import pymongo
import socket

conn = pymongo.MongoReplicaSetClient(
    'example01.com, example02.com',
    replicaSet='rs1',
    read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED,
)
db = conn.reports
```

Now call psutil for every piece of data you want.

```python
def main():
    cpu = psutil.cpu_times_percent()
    disk_root = psutil.disk_usage('/')
    phymem = psutil.phymem_usage()
    virtmem = psutil.virtmem_usage()
```

 Create a dictionary so in contains the data in the time-series structure we need.
```python
    doc = dict()
    doc['server'] = socket.gethostname()
    doc['date'] = datetime.now()
    doc['cpu'] = {
        'user': cpu.user, 
        'nice': cpu.nice,
        'system': cpu.system, 
        'idle': cpu.idle,
        'irq': cpu.irq
    }

    doc['disk_root'] = {
        'total': disk_root.total, 
        'used': disk_root.used, 
        'free': disk_root.free
    }
    doc['phymem'] = {
        'total': phymem.total, 
        'used': phymem.used, 
        'free': phymem.free
    }
    doc['virtmem'] = {
        'total': virtmem.total, 
        'used': virtmem.used, 
        'free': virtmem.free
    }
```

 Finally, add that dictionary as a document into the corresponding MongoDb collection.

```python
    if doc['server'] == 'example01.com':
        db.example01.insert(doc)
    elif doc['server'] == 'example02':
        db.example02.insert(doc)
```

Now you have the code to get the data and the database collections in which to store it. All that's left to do for this part is to automatically run the code:
Set up a cron job to run the script every 5 minutes on each server you want to monitor:

```bash
*/5 * * * * /path/to/psutil_script
```

Each mongoDB collection contains 48 hours of system performance data about the corresponding server. 

### Part 2: Display the Data with jqplot {: .article-title}

The complete code is in the GitHub project, but here is a snippet of how `jqplot` is set up to show the data. The machine `example0` runs the web server that will return the json load data. Again, the web server could be on any machine, in my example, it happens to be one of the machines being monitored. 

The complete code is in the file `psmonitor.js` and it all follows the same pattern:
1. Make the AJAX call to the server
2. Put the data you want to chart into a variable
3. Pass the variable to `jqplot`.

```javascript
$(document).ready(function(){
var jsonData = $.ajax({
      async: false,
      url: "http://example01/load/example01",
      dataType:"json"
    });

var cpu_user = [jsonData.responseJSON['cpu_user']];

$.jqplot('cpu_user',  cpu_user, {
    title: "CPU User Percent: EXAMPLE01",
    highlighter: {show: true, sizeAdjust: 7.5},
    cursor: {show: false},
    axes:{xaxis:{renderer:$.jqplot.DateAxisRenderer, 
        tickOptions:{formatString:"%a %H:%M"}}},
    series:[{lineWidth:1, showMarker: false}]
  });
});
```

The HTML is also simple. 
1. Read in the stylesheet
2. Write the `div` to hold each chart
3. Load the javascript.

```html
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Load Monitoring</title>
<link rel="stylesheet" type="text/css" href="/css/jquery.jqplot.css" />
<style>div {margin:auto;}</style>
</head>
<body>
    <div id="cpu_user" style="height:400px;width:800px; "></div>

<script src="http://code.jquery.com/jquery-latest.min.js" ></script>
<script language="javascript" type="text/javascript" src="/js/jquery.jqplot.js"></script>
<script type="text/javascript" src="/js/jqplot.json2.js"></script>
<script type="text/javascript" src="/js/jqplot.dateAxisRenderer.js"></script>
<script type="text/javascript" src="/js/jqplot.highlighter.js"></script>
<script type="text/javascript" src="/js/jqplot.cursor.js"></script>
<!--[if lt IE 9]>
  <script language="javascript" type="text/javascript" src="excanvas.js"></script>
<![endif]-->
<script type="text/javascript" src="/js/psmonitor.js" />
</body>
</html>
```


### Part 3: Set up the bottle Server {: .article-title}

Create a `bottle` application to tie everything together. 

Connect to MongoDb and when it receives a request for server data, return the formatted data for the appropriate server in the response.  

```python
from bottle import Bottle
import pymongo
load = Bottle()

conn = pymongo.MongoReplicaSetClient(
    'example01.com, example02.com',
    replicaSet='rs1',
    read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED,
)
db = conn.reports
```

This is a url connection. When a request comes in, *get* the servername from the url (`server`) and create and return the proper data structure.

```python
@load.get('/<server>')
def get_loaddata(server):
    cpu_user = list()
    cpu_nice = list()
    cpu_system = list()
    cpu_idle = list()
    cpu_irq = list()

    disk_root_free = list()
    phymem_free = list()

    if server == 'example02':
        data = db.example02.find()
    elif server == 'example01':
        data = db.example01.find()

    for data in data_cursor:
        date = data['date']

        cpu_user.append([date, data['cpu']['user']])
        cpu_nice.append([date, data['cpu']['nice']])
        cpu_system.append([date, data['cpu']['system']])
        cpu_idle.append([date, data['cpu']['idle']])
        cpu_irq.append([date, data['cpu']['irq']])

        disk_root_free.append([date, data['disk_root']['free']])
        phymem_free.append([date, data['phymem']['free']])
        
    return {
            'cpu_user': cpu_user,
            'cpu_irq': cpu_irq,
            'cpu_system': cpu_system,
            'cpu_nice': cpu_nice,
            'cpu_idle': cpu_idle,
            'disk_root_free': disk_root_free,
            'phymem_free': phymem_free
            }
```



[monitor01]: ../images/monitor01.png

