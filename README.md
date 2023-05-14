# Tripcash <h1>

## Overview
Tripcash is a Python-based web application specifically designed for managing your trip finances. With Tripcash, you can effortlessly track and record all your expenses, organizing them by date and label, and conveniently view them either as a comprehensive list or summarized.

Initially, [my original project](https://github.com/fpgodoy/tripcash) was developed with the intention of deploying it on Heroku. However, due to recent changes in Heroku's pricing structure, including the discontinuation of the free tier, I have created this fork to explore alternative self-hosting options.

Similar to the original project, this application prioritizes simplicity and speed. To deliver a seamless user experience, the application intentionally excludes any images or JavaScript. Instead, the entire CSS styling is achieved using Bootstrap, ensuring an efficient and intuitive interface.

## Features
  Here are some of the key features already available in Tripcash:
  * User authentication: Tripcash allows you to register and log in to your account, so you can keep track of your expenses and trips.
  * Trip management: With Tripcash, you can create, edit, and delete trips, and keep all your expenses organized by trip.
  * Label management: Tripcash comes with four default labels (Food, Transport, Tickets, and Accommodation), but you can create, edit, and delete your own labels to better fit your travel needs.
  * Expense tracking: Tripcash lets you register all your travel expenses, including the date, label, description, and amount, and view them in a list or by label and date. You can also edit or delete your expenses if you need to make any changes.

## Objectives for upcoming features
  * Multi-Currency Support: The aim is to enhance Tripcash by introducing support for multiple currencies. This feature will enable users to seamlessly manage expenses in different currencies during their trips, providing accurate and convenient financial tracking.
  * Multi-Language Support: Tripcash aims to provide support for multiple languages to cater to a diverse user base. This feature will allow users to select their preferred language within the application, enhancing accessibility and usability for users worldwide. By offering language options, Tripcash seeks to ensure that users can comfortably interact with the application in their native language, further enhancing their experience and usability.

## Files
  * **'\_\_init\_\_.py'**: Initializes the app components.
  * **'auth.py'**: Contains all the authentication functions, including Login, Logout, Register User, and Change Password.
  * **'db.py'**: Includes the DB connection and all the DB query to create the tables and their functions.
  * **'expense.py'**: Contains the function to create a new expense.
  * **'home.py'**: Contains functions to the index and welcome page.
  * **'label.py'**: Contains all the functions to create, edit, list, and delete the labels.
  * **'list.py'**: Contains the function to list existing expenses, delete or edit them, and the function to sum and list the expenses by label and date.
  * **'Procfile'**: Declares the process types and command to run the app on the Heroku.com platform.
  * **'requirements.txt'**: Lists all the dependencies needed to run the app.
  * **'/templates/'**: Contains all the HTML pages to render using the base.html file.