<h1 align="center">Welcome to FastAPI-Todos 🌿</h1>

A small API whose task is to manage todos. It was written on FastAPI, Nginx, Docker, Gunicorn.

<h1 align="center">Installation</h1>

**1.** Clone this repository how you like it.

**2.** Create the second required .env file with the following options **(fastapi-todos/todos/.env)**.
```
SECRET_KEY, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_MOBILE_NUMBER
```

**3.1.** To test the performance of the project.
```
$ cd todos/
$ poetry install
$ pytest
```

**3.2.** In addition, you can check the quality of the code if you need it.
```
$ cd todos/
$ poetry install
$ sudo chmod a+x lint.sh
$ ./lint.sh
```

**4.** Launch docker and all needed services.
```
$ docker-compose up --build
```
