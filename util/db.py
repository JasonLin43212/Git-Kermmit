import sqlite3

DB_FILE="data/discobandit.db" # db used for this project. delete file if you want to remove all data/login info.

db = sqlite3.connect(DB_FILE) # Open if file exists, otherwise create
c = db.cursor()               # Facilitate db operations

# Creation of three tables as specified in design.pdf. Only created if missing
c.execute("CREATE TABLE if not exists edits(user TEXT, title TEXT, edit_made TEXT, content TEXT, crtime TEXT)")
c.execute("CREATE TABLE if not exists recent(title TEXT, user TEXT, crtime TEXT)")
c.execute("CREATE TABLE if not exists users(user TEXT, password TEXT)")

def getEdits(user):
	with sqlite3.connect("discobandit.db") as db: # Allows connection to db
		cur= db.cursor()
		fetchedPass= cur.execute("SELECT title from edits WHERE user = ?",(user,)).fetchall()
		