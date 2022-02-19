# Tripcash <h1>

**Tripcash is a web-based aplication, using Python, to deal with the finances of your trip.**
Using it, you can register all your expenses and, then, list or sum them by date and label.

This is my final project of [CS50 course](https://cs50.harvard.edu/x/2021/). Created to solve my own problem dealing with my trip expenses.

Made from the [tutorial available in the official Flask documentation](https://flask.palletsprojects.com/en/2.0.x/tutorial/) and prepared to deploy using Heroku.com.


## Content
### auth.py
All the authentication functions are here, including Login, Logout, Register User and Change Password.

### db.py
Includes the DB connection and all the DB query to create the tables and their functions.

### expense.py
Here is the fucntion to create a new expense.

### home.py
Functions to the index and welcome page.

### label.py
All the functions to create, edit, list and delete the labels.

### list.py
Has the function to list existing expenses, delete or edit them and the function to sum and list the expenses by label and date.

### Procfile
Declares the process types and command to run the app on Heroku.com plataform.

### requirements.txt
Lists all the dependecies to run the app.

### /templates/
All the HTML pages to render using the base.html file.