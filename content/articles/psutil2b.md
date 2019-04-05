Title: DIY System Monitoring, Part 2
Category: Python
Status: Draft
Date: 2019-Apr-13
Tags: sysadmin, how-to, web
Summary: How to use Python3, psutil, and MongoDB with Javascript for monitoring system health.

### The NodeJS Server

I set up a cluster as follows (`server.js`):

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
} else {
  const express = require('express'),
    port = process.env.PORT || 3000,
    bodyParser = require('body-parser'),
    app = express(),
    tools = require('./api/routes/toolRoutes');

  app.use(function (req, res, next) {
    if (!res.getHeader('Cache-Control')) {
      res.setHeader('Cache-Control', 'public, max-age=600');
    }
    res.header("Access-Control-Allow-Origin", "*");
    res.header('Access-Control-Allow-Methods', 'DELETE, PUT, GET, POST');
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });

  app.use(bodyParser.urlencoded({ extended: true }));
  app.use(bodyParser.json());
  tools(app);

  app.listen(port, hostname);
  console.log('api worker started on port ' + port);
}
```

The routing is pretty simple:

```javascript
'use strict';
module.exports = function (app) {
  const tool = require('../controllers/toolController');
  app.route('/api/load/:machine')
    .get(tool.get_load);
}
```

The `find` and `get_load` functions are defined in the `toolController.js` file:

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

exports.get_load = async function (req, res) {
    const server = 'myserver';
    const query = {'server': server};
    res.json( await find('monitor', query, null) );
}
```


