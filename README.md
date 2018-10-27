# Git-Kermmit
PM: Aleksandra Koroza

Maryann Foley, Mohtasim Howlader, Robin Han

Soft Dev Project 1 (Story-Telling)

### Welcome!
   Git-Kermmit has created a story-telling tool that allows the user to write, edit, and read stories. The user can also search through available stories. We hope you enjoy using our sleek new site! (More information on the design can be found [here](https://github.com/robinhanstuy/Git-Kermmit/blob/master/design.pdf))

### Instructions for setup:

#### Virtual enviornment:
- It is important to use a venv because it creates an isolated python enviornment to run code.  It allows you to 
have your dependencies installed exclusively on it, not globally. (you don't need root access!)  This is especially useful if you need to use 2 different versions of a package with 2 pieces of code.

Steps to create a venv:
1. In a terminal, go to the folder in which you want to keep your venv
2. Run `python3 -m venv EXVENV`
   1. We are using EXVENV as the name of the virtual enviornment; you can use any name you would like
3. Activate your virtual enviornment by running `source EXVENV/bin/activate`
   1. Your computer's name will now be preceded by (EXVENV).  You are now inside of the virtual enviornment. 
4. Install dependencies (see below)
5. To exit the venv, run `deactivate`
6. You can now activate your virtual enviornment from any cwd by running `source ~/ROUTE/TO/ENV/EXVENV/bin/activate`


#### Dependencies!
- sqlite3
- flask
- wheel
- os
- passlib
- datetime

Of these, flask, passlib, and wheel are the only ones not installed automatically when you install python3.
This team requested the use of passlib and datetime for this project. Datetime is used to fetch the user's current date and time ([link](https://docs.python.org/3/library/datetime.html) to primary documentation). This information is used to display when stories were last edited. Passlib is used to more securely store passwords in our database ([link](https://passlib.readthedocs.io/en/stable/) to primary documentation).  

__NOTE:__ Activate your virtual enviornment before installing this!

1. To install flask, run `pip3 install flask`
2. To install wheel, run `pip3 install wheel`
3. To install passlib, run `pip install passlib`

## Launch instructions:
1. Activate your virtual enviornment
2. Clone and cd into this repo
3. Run `python3 app.py`
4. Enjoy!


