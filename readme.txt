The folder "youtube_python" is the core Django project.
The folder youtube_python/youtube is the "App" of this Project.

To install dependencies, run:
1. pip3 install -r req.txt

To initialize the Database (sqlite3 file)
1. delete youtube_python/db.sqlite3
2. python3 manage.py makemigrations
3. python3 manage.py migrate

In order to run this project, execute:
1. cd youtube_python
2. python manage.py runserver