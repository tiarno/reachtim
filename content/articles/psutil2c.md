Title: DIY System Monitoring, Part 3
Category: Javascript
Status: Draft
Date: 2019-Apr-13
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with Javascript for monitoring system health.

This is Part 2 of an update to the original (several years old now)
[psutil and MongoDB for System Monitoring](https://reachtim.com/articles/psutil-and-mongodb-for-system-monitoring.html)

Part 1 is here:
[DIY System Monitoring, Part 1](https://reachtim.com/articles/diy-system-monitoring-part-1.html)

In Part 1, we set things up to continuously update the database with the system load
parameters we retrieved using the Python package `psutil`. Well, not exactly 
continuously, but every 5 minutes we get an update.

In this part, we'll set up a NodeJS web server to retrieve data from 
the MongoDB `monitor` collection.

### Setting up Javascript Code  {: .article-title}

In the original article, the `bottle.py` Python package was the server.
I still love that package but wanted to get know NodeJS a little better.

This time, we'll set up a NodeJS/Express web server to
handle our queries to the server and pass that data to
Chart.js to create the visualization.

First, here's a function to "humanize" the sizes we have in memory and disk space.
It will abbreviate the number and add the appropriate unit next to it. 

```javascript
function formatBytes(bytes,decimals) {
    if(bytes == 0) return '0';
    var k = 1024,
    dm = decimals <= 0 ? 0 : decimals || 2,
    sizes = ['Bytes', 'kB', 'mB', 'gB', 'tB', 'pB', 'eB', 'zB', 'yB'],
    i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
```

Next we make our call to the server for any particular machine name.
First we set up the properties on our new data structure `data` and then
make the call to the NodeJS api. Most of the code is just pushing data
from MongoDB structure into our Javascript structure. 

The one thing that's not so obvious is this line:

```javascript
data.listening = mydata.slice(-1)[0]['myserver'];
```

We have a bunch of data coming at us in an array and this picks off
the last one. Since this is capped collection, we get the data in order,
so by pulling off the last item in the array, we have the latest info
from our machine. That's what the `slice(-1)[0]['myserver']` is doing.
That value will be 'true', 'false', or 'NA' (see the psmonitor_data.py 
script if that doesn't make sense).


```javascript
async function getApiData(machine) {
    let data = {};
    data.name = machine;
    data.listening = '';
    data.cpu = [];
    data.mem = [];
    data.disk_root = [];
    data.disk_app = [];
    await fetch("http://myserver/api/load/" + machine)
        .then(stream => stream.json())
        .then(mydata => {
        data.listening = mydata.slice(-1)[0]['saslatex'];
        mydata.forEach(record => {
            data.cpu.push({
            y: record.cpu.idle,
            x: record.date
            });
            data.mem.push({
            y: record.phymem,
            x: record.date
            });
            data.disk_root.push({
            y: record.disk_root,
            x: record.date
            });
            data.disk_app.push({
            y: record.disk_app,
            x: record.date
            });
        });
        });
    return data;
    };

```

Now we've got the data, we just need to configure Chart.js so we
can look at it. See how I changed the title green if the machine is up?

```javascript
function makeChart(machine, data, kind) {
    var ctx = document.getElementById(machine+kind);
    let maxY = 100;
    switch (kind) {
        case 'cpu':
        maxY = 100;
        break;
        case 'mem':
        maxY = 32000000000; //32gb
        break;
        case 'disk_root':
        maxY = 50000000000; //50gb
        break;
        case 'disk_app':
        maxY = 100000000000; //100gb
        break;
    }
    new Chart(ctx, {
        type: 'line',
        data: {
        datasets: [{
            label: kind,
            data: data[kind],
            borderWidth: 1.0,
            borderColor: 'navy',
            pointRadius: 0,
            pointHitRadius: 3,
            fill: false
        }]
        },
        options: {
        legend: {display: false},
        title: {
            display: true,
            fontSize: 10,
            fontColor: ((data.listening === 'true' || data.listening === 'NA') ? 'green': 'red'),
            text: machine + ' (' + kind + ')',
        },

        plugins: {
            zoom:{
            zoom:{
                enabled:true,
                drag:true,
            }
            }
        },
        scales: {
            xAxes: [{
            type: 'time',
            time: {
                unit: "hour",
                displayFormats: { hour: "dddhA" },
                tooltipFormat: "MMM. DD ddd hA"
            },
            ticks: { autoSkip: false, maxTicksLimit: 5, fontSize: 8},
            position: 'bottom'
            }],
            yAxes: [{
            ticks: {
                fontSize: 8,
                suggestedMin: 0,
                suggestedMax: maxY,
                callback: function(value, index, values) {
                if (kind === 'mem' || kind === 'disk_root' || kind === 'disk_app') {
                    return formatBytes(value, 1);
                } else {
                    return value
                }
                }
            }
            }]
        }
        }
    });
    return data;
    }
```


### All Together  {: .article-title}

Our HTML looks like this:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/moment.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0/dist/Chart.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@0.7.0"></script>
  <style>
    .myserver {
      height: 300px;
      width: 900px;
    }
    canvas {
      height: 275px;
      width: 400px;
      background: ghostwhite;
      float: left;
    }
  </style>
  <title> Build Cluster Load Monitoring</title>
</head>
<body>
  <p style="font-family:sans-serif">Build cluster health. Drag to zoom. Legend is below.</p>
  <div class="myserver">
    <table>
      <tr>
        <td><canvas id="myserver00cpu"></canvas></td>
        <td><canvas id="myserver00mem"></canvas></td>
        <td><canvas id="myserver00disk_root"></canvas></td>
        <td><canvas id="myserver00disk_app"></canvas></td>
      </tr>
       <tr>
        <td><canvas id="myserver01cpu"></canvas></td>
        <td><canvas id="myserver01mem"></canvas></td>
        <td><canvas id="myserver01disk_root"></canvas></td>
        <td><canvas id="myserver01disk_app"></canvas></td>
      </tr>
    </table>
```

You can repeat that div for as many servers as you like.
We're putting a 4 charts into a table row. You can make it look as nice as you 
like. This arrangement worked for my needs.

Then at the end of the html, add the calls to our `getApiData` function:

```javascript
    <script src="./js/mychart.js"></script>
    <script>
    getApiData('myserver00')
        .then(data => makeChart(data.name, data, 'mem'))
        .then(data => makeChart(data.name, data, 'cpu'))
        .then(data => makeChart(data.name, data, 'disk_root'))
        .then(data => makeChart(data.name, data, 'disk_app'));
    getApiData('myserver01')
        .then(data => makeChart(data.name, data, 'mem'))
        .then(data => makeChart(data.name, data, 'cpu'))
        .then(data => makeChart(data.name, data, 'disk_root'))
        .then(data => makeChart(data.name, data, 'disk_app'));
```

Here, I'm only showing 2 servers. In my real situation, I have one page with
six servers and one page with ten.

