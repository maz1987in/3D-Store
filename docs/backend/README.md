# store3d backend

~/store3d-backend

    |-- __init__.py
    |-- run.py	    	    # our run app file
    |-- config.py   	    # our config file with database connection
    |-- .env                # env url (db url)
    # Our Application Modules
    |-- /app
        |-- __init__.py     # blueprint registration
        |-- /users
            |-- __init__.py # empty file
            |-- model.py    # database table
            |-- service.py  # service and logic layer between database and api
            |-- routes.py   # routes of the api methods
        |-- /setting
            |-- __init__.py # empty file
            |-- model.py    # database table
            |-- service.py  # service and logic layer between database and api
            |-- routes.py   # routes of the api methods
    |-- /...
        |-- __init__.py
            |-- ....py
            |-- ....py
    |__ ..
    |__ ..
    |__ ..
    |__ .


**to use the code:**

1. clone the restore3ditory
2. pull the code
3. use develop branch
4. make your changes
5. push the code to development branch


# Python virtual environment
```
#pip install virtualenv
#virtualenv env
# windows
# python -m virtualenv env
# New
python -m venv env
```
In windows
```
Set-ExecutionPolicy Unrestricted -Scope Process # run this command in powershell if you get error
```
Then
```
.\env\Scripts\activate
```
Others
```
source env/bin/activate
```

TO close ENV
```
deactivate
```

To install all lib
```
pip install -r requirements.txt
```

# Docker
```
docker build . --tag store3d-api:latest
```
# # Docker Comstore3de
```
docker-comstore3de up -d
```

# Running Migration
```
alembic upgrade head
```


