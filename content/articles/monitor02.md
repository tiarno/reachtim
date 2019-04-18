Title: DIY System Monitoring, Part 2
Category: Python
Status: Draft
Date: 2019-Apr-13
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with Javascript for monitoring system health.

This is an update to the original (several years old now)
[psutil and MongoDB for System Monitoring](https://reachtim.com/articles/psutil-and-mongodb-for-system-monitoring.html)

The code for this article and the other two parts will become available on my
[GitHub Repo](https://github.com/tiarno/psmonitor)

The old version is the `python2` branch. The default branch (`master`) has the code
we're going over in this article. The first part and second part is there now.

### Introduction {: .article-title}

This three-part article enables you to create your own system-monitoring web page.

Part 1 covered the Python data gathering part: [DIY System Monitoring, Part 1: Python](https://reachtim.com/articles/diy-system-monitoring-part-1-python.html)

Part 2, this part, will cover the Node/Express web server

Part 3 will cover the JS/HTML front-end, *DIY System Monitoring, Part 3: Visualization*

### The NodeJS Server

This is how I always set up a NodeJS server. 

The directory structure is as follows::

  myapp/
    server.js
    utils.js
    api/
      controllers/toolController.js
      routes/toolRoutes.js

- `server.js` file starts the server, applies middleware, 
   integrates the app we're working on.
- `utils.js` is where I keep functions needed for database interactions
- `api/controllers` is where the app functionality lives, with a controller for
  each app.
- `api/routes` contains the routes or urls that the server will respond to, with
  one route file for each app.

We just have this one app for now so it's a pretty simple setup. It's easy to
add more apps later when you have a new idea you want to try out. Set up a route
file, a controller file and restart your server.


You have a lot of options for setting up a NodeJS server. You can start it with a single
instance using a single thread or you can use a cluster of processes in case the load
gets heavy. I have a few apps running on my server and never know what the load is going
to be like, so I set mine up as a cluster. Using the aptly named `cluster` module.

I set up a cluster as follows (`server.js`). 

```javascript
'use strict';
const cluster = require('cluster');

if (cluster.isMaster) {
  const cpuCount = require('os').cpus().length;
  for (let i = 0; i < cpuCount; i++) {
    cluster.fork();
  }
  cluster.on( 'online', function( worker ) {
    console.log( 'Worker ' + worker.process.pid + ' is online.' );
  });

  cluster.on('exit', function(worker, code, signal) {
    console.log('Worker %d died.', worker.id);
    cluster.fork();
  });
} 
```
If this instance is the master instance (the first one to execute), fork 
off as many worker NodeJS processes as you have CPUs.

As each process comes up, tell us about it on the console.
Likewise, if a process dies/exits, tell us about it on the console (and fork a new one).

```javascript
else {
  const express = require('express'),
    port = process.env.PORT || 3000,
    bodyParser = require('body-parser'),
    app = express(),
    tools = require('./api/routes/toolRoutes');

  app.use(function (req, res, next) {
    if (!res.getHeader('Cache-Control')) {
      res.setHeader('Cache-Control', 'public, max-age=600');
    }
    res.header("Access-Control-Allow-Origin", "localhost:80");
    res.header('Access-Control-Allow-Methods', 'DELETE, PUT, GET, POST');
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });
```
If this instance is not the master, we're in the `else` clause and
we're a worker process, so set up `express` to listen on port 3000.
Create an app called `app`, and load our routes.

For middleware (`app.use`), set some cache-control settings and allow for who you'll
accept connections from and what they can send you (methods and headers).

#### CORS

Something you'll see a lot in *Getting Started* tutorials is to set `Access-Control-Allow-Origin`
to `*`, a wildcard allowing for any origin. All I'll say about that here is that
it is usually a bad idea. 
See this article on [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
for details. 

Here, I've set the only origin allowed is `localhost` because the only 
request we expect is from the html file we'll create in the last part of this series
and we'll be hosting it on the same server, `localhost`.

#### Loading our custom app


```javascript
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(bodyParser.json());
  tools(app);

  app.listen(port, hostname);
  console.log('api worker started on port ' + port);
}
```
Finally we set up our app with the ability to parse JSON from the request body,
set up our local route and controller `tools` and start listening on port 3000.
Every instance will perform the same steps. 


The routing is pretty simple:

```javascript
'use strict';
module.exports = function (app) {
  const tool = require('../controllers/toolController');
  app.route('/api/load/:machine')
    .get(tool.get_load);
}
```

When the server receives a request on port 3000 with a url starting with 

```javascript
/api/load/somestring
```
it will send whatever `somestring` is as the value of the `machine` variable
to the `tool` controller and call its `get_load` function.


The `find` and `get_load` functions are defined in the `toolController.js` file:

You can forget about using `utils.js` and put the database functinality
directly in the `toolController.js` file if you want. But going on the
assumption that you may use your server for other ideas in the future,
it's nice to put database interactions in a separate file and make your
controller as tiny and simple as possible.

In the `utils.js` file, create a connection to your MongoDB and define
the `find` function. It takes the name of a collection, a query to 
select records, and, optionally, a projection that massages the returned
data into the format you want. For this app we don't need a projection
since the data is exactly formed as want it. If you have a more complex
structure, check out the docs on queries and projection in the MongoDB
[docs](https://docs.mongodb.com/manual/reference/operator/query/).

```javascript
'use strict';
const MongoClient = require('mongodb').MongoClient;
const url = 'mongodb://myserver';

const find = function (collection_name, query, projection){
  return new Promise((resolve, reject) =>{
    MongoClient.connect(url, function (err, client) {
      const db = client.db('myserver');
      const collection = db.collection(collection_name);
      collection.find(query, projection).toArray(function (err, docs) {
        if (err) { console.log('error dammit'); reject(err);}
        resolve(docs);
      });
    });
  });
}
```

Finally, the good part we've been working toward.
Behold its simplicity! We load the `find` function
from `utils.js` and ask for all the records (data documents) in 
the database for the specified server.

```javascript

exports.get_load = async function (req, res) {
    const server = 'myserver';
    const query = {'server': server};
    res.json( await find('monitor', query, null) );
}
```

You query your server with localhost:3000/api/load/server00 and it will 
return an array of json data containing the load information we have
been recording using the Python `psutil` package from the first part 
of this article.

### Unexpected Crash?

Things don't always go smoothly and your server may die. We would like
it to at least try to get back up, so consider starting your server
with a wrapper like `forever` or `pm2`. Here are some docs on both:

- [forever](https://github.com/foreverjs/forever)
- [pm2](http://pm2.keymetrics.io/)

I start mine with `forever` like this:

```javascript
forever start server.js
```

With this, we have a robust NodeJS server laid out in a way that is easy
to maintain or add capability to later on. It has a single method
to connect to the MongoDB database but for now that's all we need.

Now we're constantly saving load data from our collection of servers,
loading into our database, and we have an API server to retrieve the
data as needed.

Next time, we'll put together a simple HTML page with some Javascript to 
finally visualize the data for each server.

