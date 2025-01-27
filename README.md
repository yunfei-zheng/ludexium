# ludexium
Ludexium, a social cataloging app for video games.

The name is inspired by the Latin word for game, *ludus*.

This is my submission for the Choose Your Own Adventure Challenge for the DALI Lab.

Used Resources:
I implemented a database for user information.
I query the IGDB (Internet Games Database) for video game info,
which I accessed using Python's [igdb-api-v4](https://github.com/twitchtv/igdb-api-python)

Also used: [ChartJS plugin for colors](https://github.com/kurkle/chartjs-plugin-autocolors)

# How to Run

Setup Instructions

To run Ludexium locally, follow these steps:

Clone the repository:

```git clone https://github.com/yourusername/ludexium.git```

Navigate to the project directory:

```cd ludexium```

Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

Install dependencies:

```pip install -r requirements.txt```

Initialize the database:

```flask db init
flask db migrate
flask db upgrade
```

Run the application:

```flask run```

Open your browser and navigate to:

```http://localhost:5000```



# Borrowings:
I also utilized parts of the templates in that tutorial, including the user login system, but everything else is new functionality.
Also, I utilized some of the CSS from [this tutorial](https://python-web.teclado.com/section14/) for Dark Mode/Light Mode switching.

# My Learning Journey:
Mainly learned Flask from [Miguel Grinberg's Flask Mega-Tutorial.](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

Since I was already familiar with Python, I chose to write the backend in it, and Flask seemed like a great framework to start with. This project marks my first experience working with backend development for a real project.

I implemented JavaScript for frontend interactivity. Although I had limited experience with JavaScript before this project, I was able to learn and apply it effectively to enhance the user experience.

I used SQLite for this project, which was my first experience working with SQL tables and databases. The database stores information about users, posts, and games.

Capabilities include the ability to pick games from the IGDB database and log how many hours you have played, and see the information presented visually using ChartJS.

# Additional Notes

I don't think the email verification system actually works but it is not something I made myself anyway.
