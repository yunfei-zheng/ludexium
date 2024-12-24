# ludexium
Ludexium, a social cataloging app for video games.

The name is inspired by the Latin word for game, *ludus*.

This is my submission for the Choose Your Own Adventure Challenge for the DALI Lab.

Used Resources:
I implemented a database for user information.
I query the IGDB (Internet Games Database) for video game info,
which I accessed using Python's [igdb-api-v4](https://github.com/twitchtv/igdb-api-python)

Also used: [ChartJS plugin for colors](https://github.com/kurkle/chartjs-plugin-autocolors)

Borrowings:
I also utilized parts of the templates in that tutorial, including the user login system, but everything else is new functionality.
Also, I utilized some of the CSS from [this tutorial](https://python-web.teclado.com/section14/) for Dark Mode/Light Mode switching.

My Learning Journey:
Mainly learned Flask from [Miguel Grinberg's Flask Mega-Tutorial.](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

Since I was pretty familiar with Python, I decided to write the backend in it.
So I chose the Flask framework, which I had never worked with before this.
Actually, this is my first time doing backend for any kind of real project.

An SQLite database. This is also my first experience working with SQL tables and any database.
I store information about users, posts, games.

I also implemented JavaScript for frontend interactivity which I didn't have much experience with before.