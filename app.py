import datetime,os

import sqlite3
import passlib
from passlib.hash import pbkdf2_sha256
from flask import Flask, render_template, request, session, url_for, redirect, flash

import util.db as db


db.create()
app = Flask(__name__)
app.secret_key=os.urandom(32)# 32 bits of random data as a string

@app.route("/")
def homepage():
	'''Displays appropriate homepage based on whether user is logged in.'''
	if session.get("uname"):
		username = session["uname"]
		fetchedPass= db.getEdits(session["uname"])
		return render_template("loggedIn.html", user = username, stories = fetchedPass, lenStories = len(fetchedPass))
	return render_template("login.html",Title = 'Login')

@app.route('/logout',methods=['POST','GET'])
def logout():
	'''Route logs the user out if they are logged in'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	session.pop('uname') #ends session
	return redirect(url_for('homepage')) #goes to home, where you can login

@app.route("/authenticate", methods=['POST'])
def callback():
	'''Authentication route used to log user in'''
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	fetchedHash=db.getPwd(givenUname)
	if fetchedHash:
		if pbkdf2_sha256.verify(givenPwd, fetchedHash[0][0]):
			#fix since fetchall returns a list of tuples
			session["uname"]= givenUname #stores givern username in session
			return redirect(url_for("homepage"))
		else:
			flash('Password is wrong!')
			return redirect(url_for("homepage"))
	else:
		flash('Username is wrong!')
		return redirect(url_for("homepage"))

@app.route("/newUser", methods=['POST','GET'])
def createAcct():
	'''Used to access Create New User functionality'''
	return render_template("newUser.html")

@app.route("/addUser", methods=['POST'])
def addAcct():
	'''Adds account to db if it does not already exist'''
	givenUname=request.form["username"]
	givenPwd=request.form["password"]
	confirmPwd = request.form["confirm_password"] #prompts user twice
	hash = pbkdf2_sha256.hash(givenPwd) #user's hashed password stored in db
	if (len(givenUname)==0 or len(givenPwd)==0):
		flash('Username/Password cannot be 0 characters long')
		return redirect(url_for("createAcct"))
	if (confirmPwd != givenPwd):
		flash("Paswords don't match. Please try again!")
		return redirect(url_for("createAcct"))
	fetchedPass=db.getPwd(givenUname)
	if (len(fetchedPass) == 0):
		db.newAcct(givenUname,hash)
	else:
		flash("USER NAME ALREADY EXISTS PLS TRY AGAIN")
		return redirect(url_for("createAcct"))
	return redirect(url_for("homepage"))

@app.route("/read")
def read():
	'''Used to fetch and diplay the appropriate timestamp and content for a story'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	if not request.args.get("title"):
		return redirect(url_for("homepage"))
	givenTitle=request.args.get("title")
	fetchedUser=db.getRecent(givenTitle)
	if fetchedUser is None or len(fetchedUser)==0:
		flash(request.args.get("title") + " has not been created.")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	fetchedEdit=db.getEdit(fetchedUser,givenTitle) # fetching last edit
	fetchedHasEdited= db.getEdit(session.get("uname"),givenTitle)
	if (fetchedHasEdited is None or len(fetchedHasEdited) == 0):
		flash("YOU CAN'T READ " + request.args.get("title"))
		return redirect(url_for("homepage"))
	storyList=fetchedEdit[0].split("\n") # used to separate lines
	fetchedTime=db.getEditTime(givenTitle)
	return render_template("readStory.html", title=request.args.get("title"), story=storyList,timecr= fetchedTime)

@app.route("/unwrittenStories",methods=['POST','GET'])
def write():
	'''Used to determine which stories a user may add to'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	edited =db.getEdits(session["uname"])
	edited = set([x[0] for x in edited])
	allStories=db.getAllStories()
	allStories=[x[0] for x in allStories]
	unwritten=[]
	for story in allStories:
		if story in edited:
			continue #skips over that story (doesn't append it)
		unwritten.append(story) #add to unwritten the stories the user has not written to
	return render_template("allStories.html", stories=unwritten, lenStories=len(unwritten))

@app.route("/edit")
def edit():
	'''Used to fetch timestamps and last edit made; makes sure user has not edited that story before displaying'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	if not request.args.get("title"):
		return redirect(url_for("homepage"))
	username=session["uname"]
	givenTitle=request.args.get("title")
	fetchedUser = db.getRecent(givenTitle)
	if fetchedUser is None or len(fetchedUser) == 0: #no fetched users
		flash("It seems that that story hasn't been created yet...")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	allEditors=set([x[0] for x in db.getAllEditors(givenTitle)]) # creates set of all authors of given story
	if (username in allEditors): #to check if user already edited the story
		flash("You have already edited this story")
		return redirect(url_for("homepage"))
	else:
		pastEdit=db.getEditMade(fetchedUser,givenTitle)
		fetchedTime=db.getEditTime(givenTitle)
	return render_template("editStory.html", title=givenTitle, story=pastEdit, timecr=fetchedTime) #renders template and shows user only last edit

@app.route("/editStoryAuth", methods=['POST','GET'])
def authEdit():
	'''Checks if user can edit and, if so, updates tables with user input from edit page'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	givenTitle=request.args.get("storyTitle")
	givenStory=request.args.get("storyText")
	username=session["uname"]
	fetchedUser= db.getRecent(givenTitle)# get last author
	if (fetchedUser is None or len(fetchedUser) == 0):
		flash("It seems that that story hasn't been created yet...")
		return redirect(url_for("homepage"))
	fetchedUser=fetchedUser[0]
	allEditors=set([x[0] for x in db.getAllEditors(givenStory)]) # create set of all authors of story
	if (username in allEditors):
		flash("You have already edited this story")
		return redirect(url_for("homepage"))
	else:
		pastStory=db.getEdit(fetchedUser,givenTitle)[0]
		db.makeEdit(givenTitle,username,str(datetime.datetime.now()),givenStory,pastStory)# db updated with time and user's edit
	flash("Congrats, you edited a story!")
	return redirect(url_for("homepage"))

@app.route("/create", methods=['POST','GET'])
def newStory():
	'''Returns page for creating a story if user logged in'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	return render_template("createStory.html")

@app.route("/newStoryAuth", methods=['POST','GET'])
def authStory():
	'''Updates db with new story if story does not already exists, and if user is logged in'''
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	givenTitle=request.form["storyTitle"]
	givenStory=request.form["storyText"]
	username=session["uname"]
	fetchedUser = db.getRecent(givenTitle)
	if len(givenTitle) == 0:
		flash("PLEASE ENTER A TITLE!")
		return redirect(url_for("newStory"))
	if len(givenStory) == 0:
		flash("PLEASE ADD TEXT TO YOUR STORY")
		return redirect(url_for("newStory"))
	if fetchedUser is None or len(fetchedUser) == 0:
		time = str(datetime.datetime.now())
		db.newStory(givenTitle,username, time, givenStory) #updates db with time and user's new story
	else:
		flash("STORY WITH THAT TITLE ALREADY EXISTS PLS TRY AGAIN") #titles should be unique
		return redirect(url_for("newStory"))
	flash("Congrats you added a story!")
	return redirect(url_for("homepage"))

@app.route("/search", methods = ['POST','GET'])
def searchStory():
	'''User can input exact name of story to possibly read and/or edit'''
	searchQuery=request.form["search"]
	if not session.get("uname"):
		return redirect(url_for("homepage"))
	username=session["uname"]
	fetchedStories=db.checkTitle(searchQuery)
	if (fetchedStories is None or len(fetchedStories) == 0):#checking if story exists
		flash("This Story Doesn't Exist!")
		return redirect(url_for("homepage"))
	fetchedEdit= db.getEdit(session.get("uname"),searchQuery)
	if (fetchedEdit is None or len(fetchedEdit) == 0):
		return redirect(url_for("edit", title = searchQuery))
	return redirect(url_for("read", title = searchQuery)) #user reads story if they already edited

if __name__ == "__main__":
    app.debug = True
    app.run()
