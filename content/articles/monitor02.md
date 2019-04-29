Title: DIY System Monitoring, Part 2
Category: NodeJS
Date: 2019-Apr-22
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with NodeJS/Javascript for monitoring system health.

This is an update to the original (several years old now)
[psutil and MongoDB for System Monitoring](https://reachtim.com/articles/psutil-and-mongodb-for-system-monitoring.html)

The code for this article and the other two parts will become available on my
[GitHub Repo](https://github.com/tiarno/psmonitor)

The old version is the `python2` branch.
The default branch (`master`) has the code
we're going over in this article. The first part and second part is there now.

### Introduction {: .article-title}

This three-part article enables you to create your own system-monitoring web page.

Part 1 introduced the project and 
covered the Python data gathering part: [DIY System Monitoring, Part 1: Python](https://reachtim.com/articles/diy-system-monitoring-part-1-python.html)

Part 2, this part, will cover the Node/Express web server

Part 3 will cover the JS/HTML front-end, *DIY System Monitoring, Part 3: Visualization*

### The NodeJS Server Layout

Last time, we created a mechanism to save system monitoring data into 
as MongoDB database. In this part, we create a NodeJS web server to serve
the data and static files from the database as JSON data.

This is how I always set up a NodeJS server. Using this pattern, it is easy
to understand where functionality resides and to extend it for new projects
you may come up with.

The directory structure is as follows::

    myapp/
      server.js
      static/
      api/
        utils.js
        controllers/toolController.js
        routes/toolRoutes.js

- `server.js` file starts the server, applies middleware, and integrates the app we're working on.
- `static/` is where I put static files (html, images, etc.)
- `api/utils.js` is where I keep functions needed for database interactions or other helper functions.
- `api/controllers` is where the app functionality lives, with a controller for each app.
- `api/routes` contains the routes or urls that the server will respond to, with one route file for each app.

We just have this one app for now so it's a pretty simple setup. It's easy to
add more apps later when you have a new idea you want to try out. 
You'll just set up a route file, a controller file, and restart your server.


### Server

You have a lot of options for setting up a NodeJS server. You can start it with a single
instance using a single thread or you can use a cluster of processes in case the load
gets heavy. I have a few apps running on my server and never know what the load is going
to be like, so I set mine up as a cluster. Using the aptly named `cluster` module,
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

As you can see in the code, if this instance is the master instance (the first one to execute), fork 
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
    res.header("Access-Control-Allow-Origin", "localhost:" + port);
    res.header('Access-Control-Allow-Methods', 'GET, POST');
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });
```

If this instance is not the master, we're in this `else` clause which means that
this is a worker process, so set up `express` to listen on port 3000.
Create an express application called `app`, and load the routes for the application.

For middleware (`app.use`), set some cache-control settings and allow for who you'll
accept connections from and what they can send you (methods and headers). We really only
need to accept connection from our own server and respond to GET requests. You can 
add more as your applications need them (PUT, DELETE, etc.). I've left POST in there
just in case you need it later, but we don't even need that one for this app.

#### CORS

Something you'll see in some NodeJS beginner tutorials is to set `Access-Control-Allow-Origin`
to `*`, a wildcard allowing for requests from any origin. All I'll say about that here is that
it is usually a bad idea unless you know what you're doing.

See this article on [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
for details. 

Here, I've set the only origin allowed is `localhost:3000` because the only 
request we expect is from the html file we'll create in the last part of this series
and we'll be hosting it on the same server, `localhost` on port 3000.

#### Loading our custom app

Here is the final bit of our server code.

```javascript
  app.use('/public/', express.static('static'));
  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(bodyParser.json());
  tools(app);

  app.listen(port, 'localhost');
  console.log('api worker started on port ' + port);
}
```

We use the `static` express middleware to serve static assets like html pages,
images, css files and the like. When the requesting url starts with `/public/`,
serve the static files in the directory named `static`. That is a directory path
relative to where the server is started. You can name these anything you like. 
I picked `static` for the physical directory and `public` for the url specifier.

Then we set up our app with the ability to parse JSON from the request body,
set up our local route named `tools` and start listening on port 3000.

Every instance will perform the same steps. 

### Routing

The routing is pretty simple (`routes/toolRoutes.js`). We have one route to define:

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
to the `tool` controller's `get_load` function.

### Controller

The `get_load` function is defined in the `controllers/toolController.js` file.
Here's the part we've been working toward.

```javascript
'use strict';
const find = require('../utils').find;

exports.get_load = async function (req, res) {
    const query = {'server': req.params['machine']};
    res.json( await find('monitor', query, null) );
}
```
Behold its simplicity! 

We load the `find` function from `utils.js` and export a single function
`get_load` from this controller, passing it a query document with the 
name of the machine we want data for (which comes to as the request parameter `machine`).

#### Note: 

Alternatively, you can forget using `utils.js` and put the database functionality
directly in the `toolController.js` file if you want. But going on the
assumption that you may use your server for other ideas in the future,
it's nice to put database interactions in a separate file and make your
controller as tiny and simple as possible.

### Utilities

In the `utils.js` file, create a connection to your MongoDB and define
the `find` function. It takes the name of a collection, a query to 
select records, and, optionally, a projection that massages the returned
data into the format you want.

For this app we don't need a projection
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

Let's clear up a little confusion on names. The line that specifies the `url`
is targeting the machine name that hosts our MongoDB database, on the default
port. The line that specifies the `db` variable is the connection to our 
specific MongoDB database called `myserver`. There is no connection between
the names, they're specifying two different things: the machine that Mongo is running on
and the name of the database inside Mongo where our `monitor` data collection resides.

And also please note that all references to a machine name is the fully qualified
domain name (fqdn), not a nickname.

This function will query the `myserver` database in your MongoDB database
that you set up from the first part of this project, using Python and the
`psutil` package. So far, that database has a single collection `monitor`
where your cron job has been storing data for each server you want to
monitor.

You query your server with `localhost:3000/api/load/server00` and it will 
query the `monitor` collection in the  MongoDB `myserver` database for all
records with `server = server00`. It will
return an array of json data containing the load information we have
been recording using the Python `psutil` package from the first part 
of this article.

### Test it!

Change to the directory that contains the `server.js` file and
bring up the server:

```javascript
npm start server.js
```

You should see something like this on your command line:

    > npm start server.js

    api worker started on port 3000
    api worker started on port 3000
    api worker started on port 3000
    api worker started on port 3000
    api worker started on port 3000
    Worker 22732 is online.
    Worker 21532 is online.
    Worker 13440 is online.
    Worker 22696 is online.
    Worker 4076 is online.
    Worker 17760 is online.
    Worker 20780 is online.
    api worker started on port 3000
    Worker 21608 is online.
    api worker started on port 3000
    api worker started on port 3000

Open a browser on the same machine and request data from one of the 
servers you want to monitor (I'm using `myserver00` as mine, but yours might
be `accounts.example.com` say, it just needs to match the fqdn for one of the
servers your cron job is running on).

And in your browser you should see data that looks something like this (pretty-printed for this example):

    {
      "_id": "5cba1ab2c2ad02251845d8",
      "server": "myserver00.example.com",
      "date": "2019-04-19T15:00:02.071Z",
      "disk_app": 84642496512,
      "disk_root": 43876798464,
      "memory": 24355532800,
      "cpu": 5.1,
      "myapp": "true"
    }, {
      "_id": "5cba1bdec2ad038348cde8",
      "server": "myserver00.example.com",
      "date": "2019-04-19T15:05:01.971Z",
      "disk_app": 84642496512,
      "disk_root": 43876818944,
      "memory": 24369385472,
      "cpu": 1.4,
      "myapp": "true"
    }, 


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

### Conclusion

With this, we have a robust NodeJS server laid out in a way that is easy
to maintain or to add capability to later on. It has a single method
to connect to the MongoDB database, but for now that's all we need.

Now we're constantly saving load data from our collection of servers,
loading into our database, and we have an API server to retrieve the
data as needed.

Next time, we'll put together a simple HTML page with some Javascript to 
finally visualize the data for each server.
