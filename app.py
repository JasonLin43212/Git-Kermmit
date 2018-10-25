from flask import Flask, render_template, request, session, url_for, redirect, flash
import util.db as db
import os # Used for random key
import sqlite3
import passlib
from passlib.hash import pbkdf2_sha256
import datetime


db.create()

app = Flask(__name__)
app.secret_key=os.urandom(32)# 32 bits of random data as a string

# Root route. Displays appropriate homepage based on whether user is logged in.
@app.route("/")
def homepage():
	if session.get("uname"):
		username = session["uname"]
		fetchedPass= db.getEdits(session["uname"])
		return render_template("loggedIn.html", user = username, stories = fetchedPass, lenStories = len(fetchedPass))
	return render_template("login.html",Title = 'Login')

#Logout route. If user is logged in, they can logout from any page.
@app.route('/logout',methods=['POST','GET'])
def logout():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	session.pop('uname') #ends session
	return redirect(url_for('homepage')) #goes to home, where you can login

# Authentication route.
@app.route("/authenticate", methods=['POST'])
def callback():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	fetchedHash=db.getPwd(givenUname)
	if fetchedHash:
		print("it exists")
		if pbkdf2_sha256.verify(givenPwd, fetchedHash[0][0]):
			print(fetchedHash)
			# access first tuple of tuples
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

# route used upon clicking create user button
@app.route("/newUser", methods=['POST','GET'])
def createAcct():
	return render_template("newUser.html")

# Adds account to db and checks if it exists
@app.route("/addUser", methods=['POST'])
def addAcct():
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	confirmPwd = request.form["confirm_password"] #prompts user twice
	hash = pbkdf2_sha256.hash(givenPwd)
	fetchedPass=db.getPwd(givenUname)
	print(len(fetchedPass))#diagnostic
	if (confirmPwd != givenPwd):
		flash("Paswords don't match. Please try again!")
		return redirect(url_for("createAcct"))
	elif (len(fetchedPass) == 0):
		db.newAcct(givenUname,hash)
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
	givenTitle=request.args.get("title")
	fetchedUser=db.getRecent(givenTitle)
	if fetchedUser is None or len(fetchedUser)==0:
		flash(request.args.get("title") + " has not been created.")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	fetchedEdit=db.getEdit(fetchedUser,givenTitle)
	fetchedHasEdited= db.getEdit(session.get("uname"),givenTitle)
	if (fetchedHasEdited is None or len(fetchedHasEdited) == 0):
		flash("YOU CAN'T READ " + request.args.get("title"))
		return redirect(url_for("homepage"))

	storyList=fetchedEdit[0].split("\n") ## was unable to insert <br> or /n into jinja templates so do this instead
	###### could possibly do something so that you could see your own edit
	fetchedTime=db.getEditTime(givenTitle)
	return render_template("readStory.html", title=request.args.get("title"), story=storyList,timecr= fetchedTime)

# route used to determine which story a user can add to.
@app.route("/unwrittenStories",methods=['POST','GET'])
def write():
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	edited =db.getEdits(session["uname"])
	edited = set([x[0] for x in edited]) #converts tuple of all titles from edits from current user into a set
	allStories=db.getAllStories()
	allStories=[x[0] for x in allStories] #converts tuple of all titles from recent into a list
	unwritten=[]
	for story in allStories:
		if story in edited: #if a story from allStories in in edited, constant look-up time
			continue #skips over that story (doesn't append it)
		unwritten.append(story) ##add to unwritten the stories the user has not written to
	print(unwritten)
	return render_template("allStories.html", stories=unwritten, lenStories=len(unwritten))

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
	fetchedUser = db.getRecent(givenTitle)
	print("fetchedUser:",fetchedUser)
	if fetchedUser is None or len(fetchedUser) == 0:
		flash("It seems that that story hasn't been created yet...")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	allEditors=set([x[0] for x in db.getAllEditors(givenTitle)]) # creates set of all authors of given story
	print("allEditors:",allEditors)
	if (username in allEditors): #to check if user already edite the story
		flash("You have already edited this story")
		return redirect(url_for("homepage"))
	else:
		pastEdit=db.getEditMade(fetchedUser,givenTitle)
		fetchedTime=db.getEditTime(givenTitle)
	print("requesting title",request.args.get("title"))
	return render_template("editStory.html", title=givenTitle, story=pastEdit, timecr=fetchedTime) #renders template and shows user only last edit

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
	fetchedUser= db.getRecent(givenTitle)#get last author
	print("fetchedUser:",fetchedUser)
	if (fetchedUser is None or len(fetchedUser) == 0):
		flash("It seems that that story hasn't been created yet...")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	allEditors=set([x[0] for x in db.getAllEditors(givenStory)]) # create set of all authors of story
	print("allEditors:",allEditors)
	if (username in allEditors):
		flash("You have already edited this story")
		return redirect(url_for("homepage"))
	else:
		pastStory=db.getEdit(fetchedUser,givenTitle)[0]
		db.makeEdit(givenTitle,username,str(datetime.datetime.now()),givenStory,pastStory)
	flash("Congrats, you edited a story!")
	return redirect(url_for("homepage"))

# returns page for creating a story if logged in
@app.route("/create", methods=['POST','GET'])
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
	fetchedUser = db.getRecent(givenTitle)
	#print(len(fetchedPass))
	print(givenTitle)
	print(givenStory)
	if len(givenTitle) == 0:
		flash("PLEASE ENTER A TITLE!")
		return redirect(url_for("newStory"))
	if len(givenStory) == 0:
		flash("PLEASE ADD TEXT TO YOUR STORY")
		return redirect(url_for("newStory"))
	if fetchedUser is None or len(fetchedUser) == 0:
		print("len is 0 in newStoryAuth")
		time = str(datetime.datetime.now())
		db.newStory(givenTitle,username, time, givenStory)
	else:
		flash("STORY WITH THAT TITLE ALREADY EXISTS PLS TRY AGAIN")
		return redirect(url_for("newStory"))
	flash("Congrats you added a story!")
	return redirect(url_for("homepage"))

# in the case that the list of stories is too extensive, user can search through stories to read and edit
@app.route("/search", methods = ['POST','GET'])
def searchStory():
	searchQuery=request.form["search"]
	print(searchQuery)
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	username=session["uname"]
	fetchedStories=db.checkTitle(searchQuery)
	print(fetchedStories)
	if (fetchedStories is None or len(fetchedStories) == 0):
		flash("This Story Doesn't Exist!")
		return redirect(url_for("homepage"))
	fetchedEdit= db.getEdit(session.get("uname"),searchQuery)
	print(fetchedEdit)
	if (fetchedEdit is None or len(fetchedEdit) == 0):
		return redirect(url_for("edit", title = searchQuery))
	return redirect(url_for("read", title = searchQuery))

if __name__ == "__main__":
    app.debug = True
    app.run()
