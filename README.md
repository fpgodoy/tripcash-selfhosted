# Tripcash <h1>

### Video Demo: https://youtu.be/pjZw4wXE7mQ

## Description:
**Tripcash is a web-based aplication, using Python, to deal with the finances of your trip.**
The project is a webpage where you can register all your travel expenses and, then, list or sum them by date and label.

It's made from the [tutorial available in the official Flask documentation](https://flask.palletsprojects.com/en/2.0.x/tutorial/).

Once I would like to deploy it using Heroku, it was needed to use PostgreSQL instead of SQLite3.

To make it simple and fast to use, it doesn't have any image neither Javascript. All the CSS is made using Bootstrap.

This is my final project of [CS50 course](https://cs50.harvard.edu/x/2021/), available to test on https://tripcash.herokuapp.com .

## How to use
In the home page you can login or register a new user. To register, type a username and a password (twice). For security, all the passwords are encripted.

Once registered, you will be presented to a welcome page to create your first trip. Then, you can start to use the app selecting the created trip in the menu.

After select the trip you will be looking to the main page. From here, you can do everything about your expenses. On the top section you have the expenses options, where you can register a new expense, list the existing expenses and see a sum of them by label or date.

On the bottom section, you have some configuration options to manage the trips and labels you've created or edit them.

To register your first expense, just click on New. So, you can just fill the form and click on the green button. Don't forget to choose a label to your expense. Once registered, you will see the list with all the registered expenses in this trip.

Here you can edit ou delete each expense, or create another one clicking in New Expense.

After you have registered some expenses, on the main page, click in Total to see the sum of your expenses grouped by the On te bottom, there is a menu to filter the total bbelow y date.

Back to thename  main page, on the configuration options you can manage your trips using the corresponding button. Filling the form you create another  trip and with the buttons below you can change the name or delete any of your trips.

**Important: Deleting a trip will delete all the corresponding expenses too.**

On the Labels page, you can create new labels or edit and delete the existing ones. By default, every new user starts with 4 labels to Food, Transport, Tickets and Accomodation expenses.

The page works like the Trips one, but the expenses related to a deleted label will be grouped in a new label named "others".

## Content
### auth.py
All the authentication functions are here, including Login, Logout, Register User and Change Password.

### db.py
Includes the DB connection and all the DB query to create the tables and their functions.

### expense.py
Here is the function to create a new expense.

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