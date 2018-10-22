from flask import Flask, render_template, request, session, url_for, redirect, flash
import os # Used for random key
import sqlite3


DB_FILE="discobandit.db" # db used for this project. delete file if you want to remove all data/login info.

db = sqlite3.connect(DB_FILE) # Open if file exists, otherwise create
c = db.cursor()               # Facilitate db operations

app = Flask(__name__)
app.secret_key=os.urandom(32)# 32 bits of random data as a string

# Creation of three tables as specified in design.pdf. Only created if missing
c.execute("CREATE TABLE if not exists edits(user TEXT, title TEXT, edit_made TEXT, content TEXT)")
c.execute("CREATE TABLE if not exists recent(title TEXT, user TEXT)")
c.execute("CREATE TABLE if not exists users(user TEXT, password TEXT)")

# Root route. Displays appropriate homepage based on whether user is logged in.
@app.route("/")
def homepage():
	if session.get("uname"):
		username = session["uname"]
		with sqlite3.connect("discobandit.db") as db: # Allows connection to db
			cur= db.cursor()
			fetchedPass= cur.execute("SELECT title from edits WHERE user = ?",(username,)).fetchall()
		return render_template("loggedIn.html", user = username, stories = fetchedPass, lenStories = len(fetchedPass))
	return render_template("login.html",Title = 'Login')

#Logout route. If user is logged in, they can logout from any page.
@app.route('/logout')
def logout():
    session.pop('uname') #ends session
    return redirect(url_for('homepage')) #goes to home, where you can login

# Authentication route.
@app.route("/authenticate", methods=['POST'])
def callback():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT password from users WHERE user = ?",(givenUname,)).fetchall()
		if fetchedPass:
			print("it exists")
			if fetchedPass[0][0] == givenPwd:# access first tuple of tuples
				#fix since fetchall returns a tuple of tuples
				session["uname"]= givenUname
				if session.get("error"):# for when there is no error
					session.pop("error")
				return redirect(url_for("homepage"))
			else:
				session["error"]=2# error 2 means password was wrong
				return redirect(url_for("homepage"))
		else:
			print("it doesn't")
			session["error"]=1
			return redirect(url_for("homepage"))#error 1 means username was wrong

# route used upon clicksing create user button
@app.route("/newUser", methods=['POST','GET'])
def createAcct():
	return render_template("newUser.html")

# Adds account to db and checks if it exists
@app.route("/addUser", methods=['POST'])
def addAcct():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	confirmPwd = request.form["confirm_password"] #prompts user twice
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT password from users WHERE user = ?",(givenUname,)).fetchall()
		print(len(fetchedPass))#diagnostic
		if (confirmPwd != givenPwd):
			flash("Paswords don't match. Please try again!")
			return redirect(url_for("createAcct"))
		elif (len(fetchedPass) == 0):
			cur.execute("INSERT INTO users VALUES(?,?)",(givenUname,givenPwd))
		else:
			flash("USER NAME ALREADY EXISTS PLS TRY AGAIN")
			return redirect(url_for("createAcct"))
	return redirect(url_for("homepage"))

# route used to fetch last line contributed to story and to select titles user can contribute to
@app.route("/read")
def read():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	if not request.args.get("title"):
		return redirect(url_for("homepage"))
	print(request.args.get("title"))
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT user from recent WHERE title = ?",(request.args.get("title"),)).fetchone()[0]
		fetchedPass2= cur.execute("SELECT content from edits WHERE user = ? AND title=?",(fetchedPass,request.args.get("title"),)).fetchone()
	storyList=fetchedPass2[0].split("\n") ## was unable to insert <br> or /n into jinja templates so do this instead
	###### could possibly do something so that you could see your own edit
	return render_template("readStory.html", title=request.args.get("title"), story=storyList)

# route used to determine which story a user can add to.
@app.route("/unwrittenStories")
def write():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT title from edits WHERE user = ?",(session["uname"],)).fetchall() # fetches all titles in edits made by current user
		written=set([x[0] for x in fetchedPass]) #converts tuple of all titles from edits from current user into a set
		fetchedPass2= cur.execute("SELECT title from recent").fetchall() #all titles in recent
		allSt=[x[0] for x in fetchedPass2] #converts tuple of all titles from recent into a list
		unwritten=[]
		for x in allSt: #for each title in recent
			print(x)
			if x in written: #if a story from allSt is in written, constant look-up time
				continue #skips over that story (doesn't append it)
			unwritten.append(x) ##add to unwritten the stories the user has not written to
		print(unwritten)
		return render_template("allStories.html", stories=unwritten, lenStories=len(unwritten))
	return redirect(url_for("homepage"))

#used for diplaying which stories the user can contribute to and access editing stage
@app.route("/edit")
def edit(): # make sure that they cant edit one (check edited stories before allowing them to submit)
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	if not request.args.get("title"):
		return redirect(url_for("homepage"))
	username=session["uname"]
	givenTitle=request.args.get("title")
	print("giventitle:",givenTitle)
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedUser= cur.execute("SELECT user from recent WHERE title = ?",(givenTitle,)).fetchone() #fetches the user who wrote the story
		print("fetchedUser:",fetchedUser)
		if (len(fetchedUser) == 0):
			print("5 len of fetcheduser is 0")
			flash("It seems that that story hasn't been created yet...")
			return redirect(url_for("homepage"))
		allEditors=set([x[0] for x in cur.execute("SELECT user from edits WHERE title = ?",(givenTitle,)).fetchall()]) # creates set of all authors of given story
		print("allEditors:",allEditors)
		if (username in allEditors): #to check if user already edite the story
			flash("You have already edited this story")
			return redirect(url_for("homepage"))
		else:
			pastEdit=cur.execute("SELECT content from edits WHERE title = ? AND user = ?",(givenTitle,fetchedUser[0],)).fetchone()[0]
	print("requesting title",request.args.get("title"))
	return render_template("editStory.html", title=request.args.get("title"), story=pastEdit) #shows user only last edit

# checks if user can edit and, if so, updates tables with user input
@app.route("/editStoryAuth", methods=['POST','GET'])
def authEdit():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	givenTitle=request.args.get("storyTitle")

	print("title",givenTitle)
	givenStory=request.args.get("storyText")
	print("story",givenStory)
	username=session["uname"]
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedUser= cur.execute("SELECT user from recent WHERE title = ?",(givenTitle,)).fetchone() #get last author of story
		print("fetchedUser:",fetchedUser)
		if (fetchedUser is None or len(fetchedUser) == 0):
			flash("It seems that that story hasn't been created yet...")
			return redirect(url_for("homepage"))
		allEditors=set([x[0] for x in cur.execute("SELECT user from edits WHERE title = ?",(givenTitle,)).fetchall()]) # create set of all authors of story
		print("allEditors:",allEditors)
		if (username in allEditors):
			flash("You have already edited this story")
			return redirect(url_for("homepage"))
		else:
			pastStory=cur.execute("SELECT content from edits WHERE title = ? AND user = ?",(givenTitle,fetchedUser[0],)).fetchone()[0]
			cur.execute("DELETE FROM recent WHERE title = ?",(givenTitle,)) # row with containing given title
			cur.execute("INSERT INTO recent VALUES(?,?)",(givenTitle,username,)) # update with correct last author of story
			cur.execute("INSERT INTO edits VALUES(?,?,?,?)",(username,givenTitle,givenStory,pastStory+"\n"+givenStory,)) #update edits with new and improved story
	flash("Congrats you edited a story!")
	return redirect(url_for("homepage"))

# returns page for creating a story if logged in
@app.route("/create")
def newStory():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	return render_template("createStory.html")

# updates table with new story if story does not alread exist and if user is logged in
@app.route("/newStoryAuth", methods=['POST','GET'])
def authStory():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	givenTitle=request.form["storyTitle"]
	givenStory=request.form["storyText"]
	username=session["uname"]

	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedUser= cur.execute("SELECT user from recent WHERE title = ?",(givenTitle,)).fetchall()
		#print(len(fetchedPass))
		if (len(fetchedUser) == 0):
			print("1: len is 0 in newStoryAuth")
			cur.execute("INSERT INTO recent VALUES(?,?)",(givenTitle,username))
			cur.execute("INSERT INTO edits VALUES(?,?,?,?)",(username,givenTitle,givenStory,givenStory))
		else:
			flash("STORY WITH THAT TITLE ALREADY EXISTS PLS TRY AGAIN")
			return redirect(url_for("newStory"))
	flash("Congrats you added a story!")
	return redirect(url_for("homepage"))

# in the case that the list of stories is too extensive, user can search through stories to read and edit
@app.route("/search", methods = ['POST','GET'])
def searchStory():
	searchQuery=request.form["search"]
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	username=session["uname"]
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT title from edits WHERE title = ?",(searchQuery,)).fetchall()
	return render_template("searchStory.html", user = username, stories = fetchedPass, lenStories = len(fetchedPass))

if __name__ == "__main__":
    app.debug = True
    app.run()
