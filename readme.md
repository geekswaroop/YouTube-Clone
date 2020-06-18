# YouTube Clone 

This is a video streaming application built using Django.

 ## Team Members
 1. K Krishna Swaroop (181CO125)
 2. Niranjan S Yadiyala (181CO136)
 
 ## Directions to Run
 
The folder "youtube_python" is the core Django project.
The folder youtube is the "App" of this Project.

To install dependencies, run:
1. myenv\Scripts\activate (Activates virtual environment)
2. python -m pip install --upgrade pip (Upgrading pip)
3. pip3 install -r requirements.txt

To initialize the Database (sqlite3 file)
1. del db.sqlite3
2. python manage.py makemigrations
3. python manage.py migrate

In order to run this project, execute:
1. python manage.py runserver
2. open http://127.0.0.1:8000/ on your browser
