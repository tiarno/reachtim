Title: The BAM Short Stack
Category: Python
Date: 2014-Sep-30
Status: Draft
Tags: how-to, web
Summary: Use BAM (Bottle, Apache, and MongoDB) to create a quick website.

This how-to article describes how you can use Bottle, Apache, and MongoDB to create a simple, understandable, and fast website. In real life applications, it will also use JavaScript, but BAMJ doesn't sound as cool. If you want to play with the code, it is available on [github](). The example is kept very simple to show the general workflow. 

[TOC]

Here are the tools:

* [Bottle](http://bottlepy.org/docs/dev/index.html) Fast WSGI micro web-framework for Python
* [Apache Web Server](http://httpd.apache.org/) Popular, secure, open-source HTTP server
* [MongoDB](http://www.mongodb.com/mongodb-overview) Leading open-source NOSQL database (BSON document based)

<span class="note">Note: </span>
Be warned if you want to use a NFS file system to house your web files, logs, or database. NFS is nice if you need to share directories with clients over a network. However, file locking is slow and that can cause problems if a program finds it cannot get a lock. It is not recommended to use NFS for logging or for MongoDB.
{: .callout}

### Overview {: .article-title}

This is what we're going to do:

1. Create a simple MongoDB database.
2. Set up the Bottle web framework.
3. Create a Bottle application that can connect (GET/POST) to the data.
4. Set up Apache and WSGI to enable the Bottle app.
5. Create HTML to view the data. With some final notes on how to handle CRUD operations on the data.

I'm assuming you have installed Bottle, the Apache HTTP server with `mod_wsgi`, and  MongoDB.

* [Bottle](http://bottlepy.org/docs/dev/index.html) This is the smallest and simplest Python web framework I have found. Django has just about everything you could ever want in a framework and this is on the other end of the spectrum. I see that Flask is really popular in the area of small footprint frameworks and I would suspect it is the most competitive framework with Bottle. I like simple things, so I chose Bottle. You might find this [question](http://stackoverflow.com/questions/4941145/python-flask-vs-bottle) on `stackoverflow` helpful if you're trying to decide.
* [Apache](http://httpd.apache.org/) Over time Apache has lost its cool factor I guess, with Node being the hot topic now. But it is a hardy, stable, and very popular tool. It is easy to install and not too hard to configure. You also need to follow the 'modwsgi' installation [guide](https://code.google.com/p/modwsgi/wiki/QuickInstallationGuide).
* [MongoDB](http://www.mongodb.org/) I really like the JSON-like structure of MongoDB documents (records). For my own needs that structure fits much better than an SQL database.

You can change out any of these if you like, the basic idea is the same.

### Create the Database {: .article-title}

Create the database in the mongo shell. We'll use a collection called `test`. Here is what it looks like from a terminal window:

    :::javascript
    > mongo servername
    MongoDB shell version: 2.4.9
    connecting to: servername/test
    rs1:PRIMARY> var people = [
        {name:'Alphonse', age: '15', height: '67', weight:'116.5'},
        {name:'Janice', age: '12', height: '54.3', weight:'60.5'},
        {name:'Sam', age: '12', height: '64.3', weight:'123.25'},
        {name:'Ursula', age: '14', height: '62.8', weight:'104.0'}
    ]
   
    rs1:PRIMARY> db.people.insert(people)
    rs1:PRIMARY> db.people.find()
    { "_id" : ObjectId("..."), "name" : "Alphonse", "age" : "15", "height" : "67", "weight" : "116.5" }
    { "_id" : ObjectId("..."), "name" : "Janice", "age" : "12", "height" : "54.3", "weight" : "60.5" }
    { "_id" : ObjectId("..."), "name" : "Sam", "age" : "12", "height" : "64.3", "weight" : "123.25" }
    { "_id" : ObjectId("..."), "name" : "Ursula", "age" : "14", "height" : "62.8", "weight" : "104.0" }

### Directory Structure {: .article-title}

In `/var/www/bottle` the directory structure looks like this. Notice the pattern? This layout makes it easy to add new applications as you need them. We have the main `wsgi` script (`bottle_adapter.wsgi`), and a single application, `people`. For every application you write, you may also have a `css` file, a `javascript` file and templates in the `views` subdirectory.


    bottle_adapter.wsgi
    people_app.py

    css/
        person_form.css

    js/
        person.js

    views/
        people/
            people.tpl
            person.tpl

To add a new application, you create the application stub in the root directory, add a `css`, `js` file if needed, add `view` subdirectory to contain the application templates. In this example we don't use any javascript or even css, but in real life you will probably want to add that in. This directory layout keeps things simple and it's easy to extend.

### Apache Configuration {: .article-title}

In the Apache `httpd.conf` file, set the `WSGIScriptAlias` and `WSGIDaemonProcess`. 
For details on `wsgi` configuration, see the [guide](https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide).
When a request comes in to our server with a url that begins with `service` the request is passed on to our bottle application.

    LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
    WSGIScriptAlias /service /var/www/bottle/bottle_adapter.wsgi
    WSGIDaemonProcess example02 processes=5 threads=25 

### The `wsgi` Adapter {: .article-title}

When Apache `httpd` calls the bottle application it will execute the `bottle_adapter.wsgi` script. As you can see, the script imports the application stubs, adds to the template path and mounts the applications. The debug attribute is set to `True` until we're ready to go production.

    :::python
    import sys, bottle
    sys.path.insert(0,'/var/www/bottle')
    import people

    bottle.TEMPLATE_PATH.insert(0, '/var/www/bottle/views/people')

    application = bottle.default_app()
    application.mount('/people', people.app)

    bottle.debug(True)
    #bottle.run(host='example02', port=8090, debug=True)

### The Skeleton of an App {: .article-title}

Every application has a similar skeleton. This is the body of the `people` application.

    :::python
    from bottle import Bottle, view, request
    from bson.objectid import ObjectId
    import pymongo

    conn = pymongo.MongoReplicaSetClient(
        'example02.unx.sas.com, example01.unx.sas.com',
        replicaSet='rs1')
    db = conn.test

The `db` is the connection to the MongoDB `test` collection where the data live. 

    :::python
    app = Bottle()

And there we have it--our `people.app` Bottle application. Not that it can do very much yet, but it is wired up now. Next, add some abilities so we can respond to URL requests, like when a `GET` request comes in on `service/people`. We'll send back a response with a list of the people in the database. 

In the following code block, the `@app` decorator corresponds to a URL *route*; it responds to a `GET` request with no further arguments (`/`); by the time the request makes it here, the URL is actually `service/people`; that is what the root URL looks like to the `people` app.

The `@view` decorator specifies the template to use to display the data in the response (that is, the template `views/people/people.tpl` ) 

The `people` function creates a cursor which gets all the records (*documents* in the MongoDB world) from the database, sorts those records on the `name` and returns them as a list under the key named `results`. 

<span class="note">Note: </span>
The `sort` function in `pymongo` operates differently from the `mongo` shell; it uses a list of tuples to sort on instead of a document. This tripped me up at first. The [documentation](http://api.mongodb.org/python/current/api/pymongo/cursor.html#pymongo.cursor.Cursor.sort) explains it well.
{: .callout}

    :::python
    @app.get('/')
    @view('people')
    def people():
        p = db.people.find().sort([('name', 1)])
        return {'results': list(p)}

Here is another route using the `@app` decorator which responds to a GET request of the form `service/people/somename`. It executes the `person` function and renders the resulting data using the `person` template (`views/people/person.tpl`).

The `person` function gets the single (or first) document with a matching `name`, converts the `_id` value to a string and renders the data with the `person` template, using the results under the key named `person`.

    @app.get('/<name>')
    @view('person')
    def person(name):
        person = db['people'].find_one({'name':name})
        person['_id'] = str(person['_id'])
        return {'person': person}

The last route for this example responds to a POST request. It creates a new dictionary populated with values from the request, converts the string `_id` value back to an ObjectID, and saves the record back to the database. It returns a bare string ("Thanks...") so the user knows the data was updated.

    @app.post('/<name>')
    def update_person(name):
        person = {'name': name}
        person['age'] = request.POST.get('age')
        person['weight'] = request.POST.get('weight')
        person['height'] = request.POST.get('height')
        person['_id'] = ObjectId(request.POST.get('_id'))
        
        db['people'].save(person)
        return 'Thanks for your data.'

### Summary: What We Have So Far {: .article-title}

A request comes in with this url:

    http://example01/service/people

That url is routed from Apache to the Bottle wsgi script and on to the `people.app` Bottle application and finally to the `/people` route. That route, in turn, invokes the `people` function, which retrieves all the MongoDB documents in the `people` database and returns them in the response under a key named `results`. Then the template view `people` takes that JSON data and renders it as the response.

A request comes in with this url:

    http://example01/service/people/Sam

If the request is a `GET`, the document with `name` = `Sam` is retrieved, the `_id` is converted to a string instead of an object (it is saved as an ObjectId in the MongoDB database). The JSON data is is returned in the response under the key named `results` and rendered by the `person` template.

If the request is a `POST`, the data is read from the request form, the `_id` is turned back into an `ObjectId` and the document is saved to the database.

### A Sample Template File  {: .article-title}

This is the template `people.tpl` which displays the data after a request to `http://example02/service/people`:

    :::html
    <!doctype html>
    <html>
    <head>
      <title>List of People</title>
    </head>
    <body>
         <h1>List of People</h1>
         <table>
            <tr><th>Name</th><th>Age</th></tr>
            %for person in results:
                <tr>
                    <td>{{person['name']}}</td>
                    <td>{{person['age']}}</td>
                </tr>
            %end for
        </table>
    </body>
    </html>

And this is the (unstyled) result:

![peoplelist][peoplelist]

To view a particular person, the logic is the same except we get back a single record: `person.tpl`. 

    :::html
    <!doctype html>
    <html>
    <head>
      <title>{{person['name']}} Stats</title>
    </head>
    <body>
      <h1>{{person['name']}} Stats</h1>
         <table>
         <tr><th>Age</th><td>{{person['age']}}</td></tr>
         <tr><th>Height</th><td>{{person['height']}}</td></tr>
         <tr><th>Weight</th><td>{{person['weight']}}</td></tr>
       </table>

    </body>
    </html>

If the url is `http://example01/service/people/Alphonse`, here is the result:

[!person][person]

### CRUD Operations {: .article-title}

Performing updates, deletes, or creating data can tricky depending on the complexity of your document records. If you have nested JSON documents, you may need some Javascript to help you with the serialization of user-input data so the result has the correct structure when it gets back to MongoDB.  More on that later. For now let's write a form that enables us to update a simple record and save it. 

First we need to view the data in a prepopulated form, then we need to update the database record with whatever changes were made in the HTML client.

We already have the python code written (the `person` and `update_person` functions), we just need the HTML page. You might call it `person_update.tpl`, and change the `@app.get(/<name>)` route to use that instead of the view-only template `person.tpl`. 

This page displays the data just as the `person` template did but now the data is inside a form. We keep the `_id` value because we must have it in order to update the database. If we don't include the `_id`, our changed data will be added to the database as a new record instead of updating the original record.


    :::html
    <!doctype html>
    <html>
    <head>
      <title>{{person['name']}} Stats</title>
    </head>
    <body>
      <h1>{{person['name']}} Stats</h1>
      <form id="persondata" name="person" method="post" action="http://ltxbld02/service/people/{{person['name']}}">
        <input type="text" name="_id" value="{{person['_id']}}" style="display: none;" />
         <table>
         <tr><th>Age</th>
          <td><input type="text" name="age" value="{{person['age']}}" /></td>
        </tr>
         <tr><th>Height</th>
          <td><input type="text" name="height" value="{{person['height']}}" /></td>
        </tr>
         <tr><th>Weight</th>
          <td><input type="text" name="weight" value="{{person['weight']}}" /></td>
        </tr>
        <tr><button type="submit">Save</button></tr>
       </table>
      </form>
    </body>
    </html>

If you have nested JSON data you will probably have to use Javascript. There are so many solutions (Angular, JQuery, JSON.parse(), that I'll just point out some links. The library I use (and I have deeply nested JSON) is [form2js](https://github.com/maxatwork/form2js). 

I haven't used these, but I came across them when I was researching how to proceed. In no particular order.

* [jquery-json](https://github.com/Krinkle/jquery-json)
* [forminator](https://github.com/DubFriend/forminator)
* [domajax](http://www.domajax.com/)
* [jquery.form.serializer](https://github.com/rdiazv/jquery.form.serializer)
* [form](https://github.com/rdiazv/jquery.form.serializer)

[peoplelist]: ../images/peoplelist.png
[person]: ../images/person.png

Here is an example of using the `form2js` library. You can use the library with arbitrarily nested JSON documents. However, you need to make a couple of changes to your Bottle app. This example template and the changed app code are in the GitHub files `alt_people.py` and `alt_person_update.tpl`.

The template file is shown here. The form itself is identical but the *submit* button now calls a Javascript function that gets the JSON data from the form which is then stringified and sent via ajax back to our URL route for updating a person (the only route in our app that accepts a POST request).

    :::javascript
    <!doctype html>
    <head>
    <title>{{person['name']}} Stats</title>
    <script type="text/javascript" src="/js/jquery-1.9.1.min.js"></script>
    <script type="text/javascript" src="/js/form2js-master/src/form2js.js"></script>
    <script type="text/javascript">
            save_data = function(evt){
                var json_data = form2js('persondata', skipEmpty=false);
                var jsonstr = JSON.stringify(json_data, null, '\t');
                $.ajax({
                    type:"POST",
                    url: 'http://example02/service/people',
                    data: jsonstr,
                    success: function(){
                        alert('Configuration saved.')
                    }
                });
            };
          (function($){
             $(function(){
            $('input[type=submit]').val('Submit').click(save_data);
          });
           })(jQuery);
       </script>
    </head>
    <body>
    <h1>{{person['name']}} Stats</h1>
    <form id="persondata" name="person">
      <input type="text" name="_id" value="{{person['_id']}}" style="display: none;" />
      <input type="text" name="name" value="{{person['name']}}" style="display: none;" />
      <table>
        <tr>
          <th>Age</th>
          <td><input type="text" name="age" value="{{person['age']}}" /></td>
        </tr>
        <tr>
          <th>Height</th>
          <td><input type="text" name="height" value="{{person['height']}}" /></td>
        </tr>
        <tr>
          <th>Weight</th>
          <td><input type="text" name="weight" value="{{person['weight']}}" /></td>
        </tr>
        <tr>
          <td><input type="submit" /></td>
        </tr>
      </table>
    </form>
    </body>
    </html>

The main change to the `people` app is the `update_person` function, which now looks like this:

    :::python
    @app.post('/')
    def update_person():
        data = request.body.read()
        person = loads(data)
        person['_id'] = ObjectId(person['_id'])
        db['people'].save(person)

Check it out on GitHub if you want to play around with it. It is very easy to add applications and get CRUD operations going on any mongoDB database.

Let me know if you have any questions or if something needs changing on the GitHub repo.
