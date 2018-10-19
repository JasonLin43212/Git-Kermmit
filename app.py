from flask import Flask, render_template, request, session, url_for, redirect, flash
import os

app = Flask(__name__)
app.secret_key=os.urandom(32)# 32 bits of random data as a string

@app.route("/")
def homepage():
	if session.get("uname"):
		username = session["uname"]
		return render_template("loggedIn.html", user = username, stories = "SOME SQLITE COMMAND TO GET CONTRIBUTED STORIES")
	return render_template("login.html",Title = 'Login')

@app.route('/logout')
def logout():
    session.pop('uname') #ends session
    return redirect(url_for('homepage')) #goes to home, where you can login


@app.route("/authenticate", methods=['POST'])
def callback():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	if givenUname=="usr":
		if givenPwd=="pwd":
			session["uname"]=givenUname
			if session.get("error"):
				session.pop("error")
		else:
			session["error"]=2#error 2 means password was wrong
		return redirect(url_for("homepage"))
	else:
		session["error"]=1
		return redirect(url_for("homepage"))#error 1 means username was wrong

@app.route("/newUser")
def createAcct():
	if not session.get("uname"):
		return render_template("newUser.html")
	return redirect(url_for("homepage"))


@app.route("/read") #title =
def read():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	return render_template("readStory.html")

@app.route("/unwrittenStories")
def write():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	return render_template("allStories.html")

@app.route("/edit")#title
def edit():
	if not session.get("uname"):
		return redirect(url_for("homepage"))


@app.route("/create")
def newStory():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	return render_template("createStory.html")

# @app.route("/newStoryAuth")
# def authStory():
#




if __name__ == "__main__":
    app.debug = True
    app.run()
