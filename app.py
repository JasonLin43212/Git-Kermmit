from flask import Flask, render_template
app = Flask(__name__)


@app.route("/")
def homepage():
	if session.get("user"):
		return render_template("loggedIn.html")
	return render_template("login.html",Title = 'Login')

@app.route("/authenticate")
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
		return redirect(url_for("home"))
	else:
		session["error"]=1
		return redirect(url_for("home"))#error 1 means username was wrong

@app.route("/newUser")
def createAcct():

@app.route("/edit", title=#title)
def edit():
	if not session.get("user"):
		return redirect(url_for("homepage"))

@app.route("/read", title=#title)
def read():
	if not session.get("user"):
		return redirect(url_for("homepage"))

@app.route("/unwrittenStories")
def write():
	if not session.get("user"):
		return redirect(url_for("homepage"))

@app.route("/create")
def newStory():
	if not session.get("user"):
		return redirect(url_for("homepage"))




if __name__ == "__main__":
    app.debug = True
    app.run()
