# Git-Kermmit
PM: Aleksandra Koroza
Maryann Foley, Mohtasim Howlader, Robin Han
Soft Dev Project 1 (Story-Telling)

### Instructions for launch

##### Virtual enviornment:
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
- os

Uses python 3


