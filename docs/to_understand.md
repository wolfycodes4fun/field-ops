# The Basics

SQLAlchemy is an Object Relational Mapper, an entity between the database (Postgres in the  
context of the following project) and the Flask application. As per the architecture, the 
**extensions.py** initializes an instance of SQLAlchemy and in the **app.py** for each service, this instance is associated via the init_app() method where it reads through the configs of the Flask app (ex- SQLALCHEMY_DATABASE_URI).  

Flask-Migrate extension is used to modify the state of the database to fit accordingly to our desired state. It creates the association between the context of the app and database using the init_app() method. 