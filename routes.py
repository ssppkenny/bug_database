from flask import Flask, render_template, request, redirect, flash
from flask_pymongo import PyMongo
from flask import Response
from base64 import b64encode, b64decode
from bson.objectid import ObjectId
from bson.binary import Binary
import sys

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://sergey:goteborg2@mycluster-jh3jq.mongodb.net/flow-reader?ssl=true&authSource=admin"
app.secret_key = 'super secret key'
mongo = PyMongo(app)

@app.route("/image/<objectid>")
def image(objectid):
    print(objectid)
    bug = mongo.db.bugs.find_one({"_id": ObjectId(objectid)})
    bytes = b64decode(bug["image"]["$binary"])
    print(bytes, file=sys.stderr)
    return Response(bytes, mimetype='image/png')

@app.route("/bug/new", methods=["POST"])
def submit_bug_json():
    if request.is_json:
        json = request.get_json()
        print(json, file=sys.stderr)
        mongo.db.bugs.insert(json, check_keys=False)
        return Response("OK")
    else:
        print(Response(401))


@app.route("/bugs")
def bugs():
    bugs = mongo.db.bugs.find()
    return render_template("bugs.html", bugs=bugs)

@app.route("/bug/submit", methods=["GET", "POST"])
def submit_bug():
    if request.method == "POST":
        print(request.files, file=sys.stderr)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        else:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
            bytes = file.read()
            form = request.form
            description = form["description"]
            bug = {"description": description, "image": {"$binary" : b64encode(bytes)}, "contenttype": file.content_type}
            print(bug)
            mongo.db.bugs.insert(bug, check_keys=False)
            return redirect(request.url)
    else:
        return render_template("submit_bug.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)


