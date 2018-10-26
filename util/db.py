import sqlite3

def create():
	DB_FILE="discobandit.db" # db used for this project. delete file if you want to remove all data/login info.
	db = sqlite3.connect(DB_FILE) # Open if file exists, otherwise create
	c = db.cursor()               # Facilitate db operations
	# Creation of three tables as specified in design.pdf. Only created if missing
	c.execute("CREATE TABLE if not exists edits(user TEXT, title TEXT, edit_made TEXT, content TEXT)")
	c.execute("CREATE TABLE if not exists recent(title TEXT, user TEXT, crtime TEXT)")
	c.execute("CREATE TABLE if not exists users(user TEXT, password TEXT)")

def getEdits(user):
	with sqlite3.connect("discobandit.db") as db: # Allows connection to db
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT title from edits WHERE user = ?",(user,)).fetchall()
	return fetchedPass

def getPwd(givenUname):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedHash= cur.execute("SELECT password from users WHERE user = ?",(givenUname,)).fetchall()
	return fetchedHash

def newAcct(givenUname,givenPwd):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		cur.execute("INSERT INTO users VALUES(?,?)",(givenUname,givenPwd)) #inserts hash version of password

def getRecent(givenTitle):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT user from recent WHERE title = ?",(givenTitle,)).fetchone()
	return fetchedPass

def getEdit(user,title):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		edit= cur.execute("SELECT content from edits WHERE user = ? AND title=?",(user,title,)).fetchone()
	return edit

def getEditTime(title):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		time=cur.execute("SELECT crtime from recent WHERE title = ?",(title,)).fetchone()[0]
	return time

def getAllStories():
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		stories=cur.execute("SELECT title from recent").fetchall() #all titles in recent
	return stories

def getAllEditors(title):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		editors=cur.execute("SELECT user from edits WHERE title = ?",(title,)).fetchall()
	return editors

def getEditMade(user,title):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		edit= cur.execute("SELECT edit_made from edits WHERE user = ? AND title=?",(user,title,)).fetchone()
	return edit

def makeEdit(title,username,time,givenStory,pastStory):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		cur.execute("DELETE FROM recent WHERE title = ?",(title,)) # row with containing given title
		cur.execute("INSERT INTO recent VALUES(?,?,?)",(title,username,time,)) # update with correct last author of story
		cur.execute("INSERT INTO edits VALUES(?,?,?,?)",(username,title,givenStory,pastStory+"\n"+"\n"+givenStory,)) #update edits with new and improved story

def newStory(title,username,time,givenStory):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		cur.execute("INSERT INTO recent VALUES(?,?,?)",(title,username,time,))
		cur.execute("INSERT INTO edits VALUES(?,?,?,?)",(username,title,givenStory,givenStory,))

def checkTitle(title):
	with sqlite3.connect("discobandit.db") as db:
		cur= db.cursor()
		fetchedTitles = cur.execute("SELECT title from recent WHERE title = ?",(title,)).fetchall()
	return fetchedTitles
	
