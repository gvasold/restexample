# cities example TEST server

`restexample` is a simple REST server I wrote for teaching REST.


## Installation

Clone the project from Github

```bash
git clone https://github.com/gvasold/restexample
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # linux/osx
venv/Scripts/activate  # windows
```

Install the required dependencies:

```bash
pip install -r requirement.txt
```

## Running

To start the server, make sure your venv is activated, then run this command:

```bash
uvicorn cities.main:app
```

While developing you might want to set the ``--reload`` option.

```
uvicorn cities.main:app --reload
```

If this does not work, because port 8000 is already in use, you can
try another port:

```
uvicorn cities.main:app --port 8888 
```

To test if the server is up and running, navigate your browser to
http://localhost:8000/redoc,
which should lead you to the OpenAPI based documentation.

If you see this page, the server is up and running, but does not contain any data yet.

## Insertig some data

To add data, cd to the ``bin`` directory and then run the python `populate_db.py` script
(make sure that the virtual environment is active!)

```bash
cd bin
python populate_db.py.
```

Now you can use the REST interface, example by navigating to 
http://localhost:8000/countries/1.

You can always reset the database by re-running the `populate_db.py` script.

If you want to get rid of all data, stop the server (``CTRL-C``) and delete the
``cities.db`` file. Then start the server again and run the `populate_db.py` script.

## Running the tests

`restexample` comes with many tests. To start the tests, enter

```bash
pytest
```

