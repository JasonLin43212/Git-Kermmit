from flask import Flask, render_template, request, session, url_for, redirect, flash
import os
import sqlite3

DB_FILE="discobandit.db" #delete before every subsequent run

db = sqlite3.connect(DB_FILE) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops

app = Flask(__name__)
app.secret_key=os.urandom(32)# 32 bits of random data as a string

c.execute("CREATE TABLE if not exists edits(user TEXT, title TEXT, edit_made TEXT, content TEXT)")
c.execute("CREATE TABLE if not exists recent(title TEXT, user TEXT)")
c.execute("CREATE TABLE if not exists users(user TEXT, password TEXT)")


@app.route("/")
def homepage():
	if session.get("uname"):
		username = session["uname"]
		with sqlite3.connect("discobandit.db") as db:
			cur= db.cursor()
			fetchedPass= cur.execute("SELECT title from edits WHERE user = ?",(username,)).fetchall()
		return render_template("loggedIn.html", user = username, stories = fetchedPass, lenStories = len(fetchedPass))
	return render_template("login.html",Title = 'Login')

@app.route('/logout')
def logout():
    session.pop('uname') #ends session
    return redirect(url_for('homepage')) #goes to home, where you can login


@app.route("/authenticate", methods=['POST'])
def callback():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	#print("read")
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()

		fetchedPass= cur.execute("SELECT password from users WHERE user = ?",(givenUname,)).fetchall()
		#print(givenUname)
		#print(fetchedPass[0][0])
		if fetchedPass:
			print("it exists")
			if fetchedPass[0][0] == givenPwd:
				#fix since fetchall returns a tuple of tuples
				session["uname"]= givenUname
				if session.get("error"):
					session.pop("error")
				return redirect(url_for("homepage"))
			else:
				session["error"]=2#error 2 means password was wrong
				return redirect(url_for("homepage"))
		else:
			print("it doesn't")
			session["error"]=1
			return redirect(url_for("homepage"))#error 1 means username was wrong

@app.route("/newUser", methods=['POST','GET'])
def createAcct():
	return render_template("newUser.html")

#adds account to db and checks if it exists
@app.route("/addUser", methods=['POST'])
def addAcct():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT password from users WHERE user = ?",(givenUname,)).fetchall()
		print(len(fetchedPass))
		if (len(fetchedPass) == 0):
			cur.execute("INSERT INTO users VALUES(?,?)",(givenUname,givenPwd))
		else:
			flash("USER NAME ALREADY EXISTS PLS TRY AGAIN")
			return redirect(url_for("createAcct"))
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

@app.route("/newStoryAuth", methods=['POST','GET'])
def authStory():
	givenTitle=request.form["storyTitle"]
	givenStory=request.form["storyText"]
	username=session["uname"]

	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		#
		fetchedUser= cur.execute("SELECT user from recent WHERE title = ?",(givenTitle,)).fetchall()
		#print(len(fetchedPass))
		if (len(fetchedUser) == 0):
			cur.execute("INSERT INTO recent VALUES(?,?)",(givenTitle,username))
			cur.execute("INSERT INTO edits VALUES(?,?,?,?)",(username,givenTitle,givenStory,givenStory))
		else:
			flash("STORY WITH THAT TITLE ALREADY EXISTS PLS TRY AGAIN")
			return redirect(url_for("newStory"))
	flash("congrats you added a story!")
	return redirect(url_for("homepage"))





if __name__ == "__main__":
    app.debug = True
    app.run()
