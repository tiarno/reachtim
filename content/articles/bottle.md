Title: How to Start Using the BAM Short Stack
Category: Python
Date: 2014-Sep-30
Status: Draft
Tags: how-to, web
Summary: Use BAM (Bottle, Apache, and MongoDB) to create a quick website.

This how-to article describes how you can use Bottle, Apache, and MongoDB to create a simple, understandable, and fast website. In real life applications, it will also use JavaScript, but BAMJ doesn't sound as cool. If you want to play with the code in this example, it is available on [github](https://github.com/tiarno/bam_example). The example is kept very simple to show the general workflow. 

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
3. Set up Apache and WSGI to enable Bottle applications.
4. Create a Bottle application that can connect (using GET/POST) to the MongoDB database.
5. Create HTML to view the data. With some final notes on how to handle CRUD operations on the data.

I'm assuming you have installed Bottle, the Apache HTTP server with `mod_wsgi`, and  MongoDB.

* [Bottle](http://bottlepy.org/docs/dev/index.html) This is the smallest and simplest Python web framework I have found. Django has just about everything you could ever want in a framework and this is on the other end of the spectrum. I see that Flask is really popular in the area of small footprint frameworks and I would suspect it is the most competitive framework with Bottle. I like simple things, so I chose Bottle. You might find this [question](http://stackoverflow.com/questions/4941145/python-flask-vs-bottle) on `stackoverflow` helpful if you're trying to decide.
* [Apache](http://httpd.apache.org/) Over time Apache has lost its cool factor I guess, and Node is the hot topic now. But it is a hardy, stable, and very popular tool. It is easy to install and not too hard to configure. You also need to follow the `modwsgi` installation [guide](https://code.google.com/p/modwsgi/wiki/QuickInstallationGuide).
* [MongoDB](http://www.mongodb.org/) I really like the JSON-like structure of MongoDB documents (records). For my own needs, that structure fits much better than an SQL database.

You can change out any of these if you like, the basic idea is the same.

### Create the Database {: .article-title}

Create our toy `people` database in the mongo shell. We'll use a collection called `test`. Here is what it looks like from a terminal window:

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

That is the data we'll connect to via Bottle/Apache.

### Bottle Directory Structure {: .article-title}

In `/var/www/bottle` the directory structure looks like this. Notice the pattern? This layout makes it easy to add new applications as you need them. We have the main `wsgi` script (`bottle_adapter.wsgi`), and a single application, `people`. For every application you write, you may also have a `css` file, a `javascript` file and templates in the `views` subdirectory.


    bottle_adapter.wsgi
    people.py

    css/
        person_form.css

    js/
        person.js

    views/
        people/
            people.tpl
            person.tpl

To add a new application:

1. create the application code file in the root directory, like `people.py`
2. mount the application in the `bottle_adapter.wsgi` file
3. add the template path in the `bottle_adapter.wsgi` file
4. add `css`, `js` files if needed
5. add a `view` subdirectory to contain the application templates. 

In this example we don't use any javascript or even css, but in real life you will probably want to add that in. This directory layout keeps things simple and separated, and it's easy to extend.

### Apache Configuration {: .article-title}

In the Apache `httpd.conf` file, set the `WSGIScriptAlias` and `WSGIDaemonProcess`. 
For details on `wsgi` configuration, see the [guide](https://code.google.com/p/modwsgi/wiki/QuickConfigurationGuide).
When a request comes in to our server with a url that begins with `service` the request is passed on to our bottle application.

    LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so
    WSGIScriptAlias /service /var/www/bottle/bottle_adapter.wsgi
    WSGIDaemonProcess example02 processes=5 threads=25 

You may need to set other parameters depending on your platform. I am on a FreeBSD machine and needed to set `WSGIAcceptMutex posixsem` in addition to the settings above.

### The `wsgi` Adapter {: .article-title}

When the Apache server gets a request that begins with `service`, the `httpd` daemon calls the bottle application; that is, it executes the `bottle_adapter.wsgi` script. As you can see below, the script imports the application code, adds to the template path and "mounts" the applications on a specific URL path. Now that `people` is mounted on the path `/people`, the application will get called for any URL that starts with `/service/people`. 

The debug attribute is set to `True` until we're ready to go production.

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

Every application will have a similar skeleton. This is the `people` application. First make the necessary imports, get a connection to the MongoDB database `test` collection and instantiate our application, `app` (known as `people.app` to the `wsgi` adapter).

    :::python
    from bottle import Bottle, view, request
    from bson.objectid import ObjectId
    import pymongo

    conn = pymongo.MongoReplicaSetClient(
        'example02.unx.sas.com, example01.unx.sas.com',
        replicaSet='rs1')
    db = conn.test

    :::python
    app = Bottle()

And there we have it--our `people.app` Bottle application, all wired up but not able to do anything yet. Let's add some abilities so we can respond to URL requests. For example, when a `GET` request comes in on `service/people`, we'll send back a response with a list of the people in the database. 

In the following code block, the `@app.get` decorator corresponds to a URL *route*; it responds to a `GET` request with no further arguments (`/`); by the time the request makes it here, the URL is actually `service/people`; that is what the root URL looks like to the `people` app.

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

Keep in mind that this is just a simple toy example; if you have a bazillion records or a gazillion requests per second, you'll want to do a lot of reading on MongoDB index creation, aggregation and filtering techniques.
{: .callout}

### Summary: What We Have So Far {: .article-title}

When a request comes in with this url:

    http://example01/service/people

that url is routed from Apache to the Bottle `wsgi` script and on to the `people.app` Bottle application and finally to the `/people` route. That route, in turn, invokes the `people` function, which retrieves all the MongoDB documents in the `people` database and returns them in the response under a key named `results`. Then the template view `people` takes that JSON data and renders it as the response.

When a request comes in with this url:

    http://example01/service/people/Sam

If the request is a `GET`, the document with `name` = `Sam` is retrieved, the `_id` is converted to a string instead of an object (it is saved as an ObjectId in the MongoDB database). The JSON data is is returned in the response under the key named `results` and rendered by the `person` template.

If the request is a `POST`, the data is read from the request form, the `_id` is turned back into an `ObjectId` and the document is saved to the database.

<span class="note">Note: </span>
With this smidgen of code and a rational directory structure, before even talking about the HTML side, we have an simple, easy-to-understand API that can send and receive JSON documents, interacting with a MongoDB backend database.
{: .callout}

### A Sample Template File  {: .article-title}

You can use plain HTML to display and update records if your underlying data has a simple structure. 

This is the view-only template `people.tpl` which displays the data after on a GET request to `http://example02/service/people`:

    :::html
    <!doctype html>
    <html>
    <head>
      <title>People</title>
    </head>
    <body>
         <h1>People</h1>
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

To view a particular person, the logic is similar, except we get back a single record: Here is the template `person.tpl`:

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

![person][person]

### CRUD Operations {: .article-title}

Performing updates, deletes, or creating data can get tricky, depending on the complexity of your document records. If you have nested JSON documents, you will need some Javascript to serialize the user-input data so the result has the correct structure when it gets back to MongoDB.  More on that later. For now let's write a form that enables us to update a simple record and save it. 

#### Simple Case {: .article-title}

First we need to view the data in a prepopulated form, then we need to update the database record with whatever changes were made in the HTML client.

We have  already written the Python code (the `person` and `update_person` functions), so we just need the HTML page. You might call it `person_update.tpl`, and change the `@app.get(/<name>)` route to use that instead of the view-only template `person.tpl`. 

This page displays the data just as the `person` template did, but now it is inside an HTML form. We keep the `_id` value because we must have it in order to update the database. If we don't include the `_id`, our changed data will be added to the database as a new record instead of updating the original record.

    :::html
    <!doctype html>
    <html>
    <head>
      <title>{{person['name']}} Stats</title>
    </head>
    <body>
      <h1>{{person['name']}} Stats</h1>
      <form id="persondata" name="person" method="post" action="http://example02/service/people/{{person['name']}}">
        <input type="text" name="_id" value="{{person['_id']}}" style="display: none;" />
        <input type="text" name="name" value="{{person['name']}}" style="display: none;" />
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


#### Complex Case {: .article-title}

If you have nested JSON data you will probably have to use Javascript. There are so many solutions that I'll just point out some links. The library I use (and I have deeply nested JSON) is [form2js](https://github.com/maxatwork/form2js). 

In no particular order, here are some similar libraries that address the same situation:

* [jquery-json](https://github.com/Krinkle/jquery-json)
* [forminator](https://github.com/DubFriend/forminator)
* [domajax](http://www.domajax.com/)
* [jquery.form.serializer](https://github.com/rdiazv/jquery.form.serializer)
* [form](https://github.com/rdiazv/jquery.form.serializer)

The following is an example of using the `form2js` library and `jquery`. You can use the library with arbitrarily nested JSON documents. However, you need to make a couple of changes to your Bottle app. This example template and the changed app code are in the GitHub files `alt_people.py` and `alt_person_update.tpl`.

In the template, the form itself is identical but the *submit* button now calls a Javascript function.

    :::html
    <!doctype html>
    <head>
    <title>{{person['name']}} Stats</title>
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

When the user clicks the `submit` button, the `save_data` function is called.
In turn, `save_data` gets the JSON data from the form, stringifies it and fires an AJAX POST back to our URL route for updating a person (the only route in our app that accepts a POST request).

    :::javascript
    <script type="text/javascript" src="/js/jquery.min.js"></script>
    <script type="text/javascript" src="/js/form2js.js"></script>
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
    </body>
    </html>

The main change to the `people` app is the `update_person` function, which now looks like the following. The function `loads` is included in the `pymongo` package that provides conversion from a string instance to a BSON document.

    :::python
    @app.post('/')
    def update_person():
        data = request.body.read()
        person = loads(data)
        person['_id'] = ObjectId(person['_id'])
        db['people'].save(person)

Check it out on [GitHub](https://github.com/tiarno/bam_example) if you want to play around with it. It is very easy to add applications and get CRUD operations going on any mongoDB database.

Let me know if you have any questions or if something needs changing on the GitHub repo.


[peoplelist]: ../images/peoplelist.png
[person]: ../images/person.png