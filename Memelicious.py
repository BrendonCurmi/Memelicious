import os
import re
from flask import Flask, render_template, request, url_for, redirect, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from profiles import hash_password, is_logged_in
from database import Profile, Memes
from variables import Variables

# UPLOAD_FOLDER = "/home/memelicious/deploy/static/img/upload"
UPLOAD_FOLDER = "static\\img\\upload"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.secret_key = Variables.secret_key

# import datetime
# expire_date = datetime.datetime.now()
# expire_date = expire_date + datetime.timedelta(days=90)
# response.set_cookie(key, guid, expires=expire_date)


@app.context_processor
def utility_processor():
    def feed1():
        return ""
    return dict(feed1=feed1)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home", indent=False)


@app.route("/get_memes", methods=["POST"])
def get_memes():
    from memes import meme_machine, random_feed

    if request.form["type"] == "1":
        if request.form["start"] == "0":
            result = meme_machine(Memes.get_latest_id(), request.form["pool"])
        else:
            result = meme_machine(int(request.form["start"]), request.form["pool"])
        return jsonify({"memes": result[0], "pool": result[1], "highestid": Memes.get_latest_id()})
    elif request.form["type"] == "2":
        result = random_feed(request.form["pool"])
        return jsonify({"memes": result[0], "pool": result[1]})


@app.route("/upload", methods=["GET", "POST"])
def upload_meme():
    if not is_logged_in() or request.method != "POST":
        return redirect(url_for("index"))
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            return redirect(url_for("index"))
        file = request.files["file"]
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == "":
            return redirect(url_for("index"))

        for file in request.files.getlist("file"):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = filename.split(".")[1]
                filename = generate_unique_name() + "." + extension
                print(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                # file.save(app.config["UPLOAD_FOLDER"] + "/" + filename)
                Memes.insert_meme(filename, session["email"])
                return redirect(url_for("uploaded_file", filename=filename))
        return redirect(url_for("index"))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_name():
    from profiles import randomise
    name = randomise(16)
    return name if not Memes.already_exists(name=name) else generate_unique_name()


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    print(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/tos")
def tos():
    return render_template("tos.html", title="Terms of Service", masthead="Memelicious Terms of Service")


@app.route("/gateway", methods=["GET", "POST"])
def gateway():
    if is_logged_in():
        return redirect(url_for("index"))
    err = ""
    if request.method == "POST":
        try:
            email = fix(request.form["email"], "@\.")
            username = fix(request.form["username"])
            password = fix(request.form["password"])
            confirm = fix(request.form["confirm"])
            if validate_email(email):
                if not Profile.already_exists(email=email):
                    if validate_username(username):
                        if not Profile.already_exists(username=username):
                            if password == confirm and password != "":
                                Profile.insert_profile(email, username, hash_password(password))
                                return render_template("gateway.html", title="Gateway")
                            else:
                                err = "Invalid Passwords Entered"
                        else:
                            err = "Username Already Exists"
                    else:
                        err = "Invalid Username Entered"
                else:
                    err = "Email Already Exists"
            else:
                err = "Invalid Email Entered"
        except Exception as e:
            email = fix(request.form["email"], "@\.")
            password = fix(request.form["password"])
            if email is not None and password is not None:
                if Profile.already_exists(email=email):
                    expected_pass = Profile.get_password_hash(email)
                    salt, pass_hash = str(expected_pass).split("$")
                    if expected_pass == str(hash_password(password, salt)):
                        session["email"] = email
                        session["username"] = Profile.get("username", email=email)
                        return redirect(url_for("index"))
                    else:
                        err = "Incorrect Email or Password"
                else:
                    err = "Incorrect Email"
            else:
                err = "Fill in all blanks"

    reg = True if request.args.get("reg") == "true" else False
    return render_template("gateway.html", title="Gateway", indent=False, reg=reg, err=err)


def fix(string, chars=""):
    return re.sub("[^a-zA-Z0-9%s\n]" % chars, " ", string)


def validate_email(email):
    return True if "@" in email else False


def validate_username(username):
    return True if len(username) < 65 else False


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("email", None)
    return redirect(url_for("index"))


@app.route("/profile/<username>")
def profile(username):
    if not Profile.already_exists(username=username):
        return redirect(url_for("index"))
    return render_template("profile.html", title="%s's Profile" % username, username=username)


if __name__ == "__main__":
    app.run()
