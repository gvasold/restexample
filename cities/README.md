# cities example TEST server

`cities` is a simple REST server I use to teach REST.


# Installation

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # linux/osx
venv/Scripts/activate  # windows
```

Install the needed dependencies:

```bash
pip install requirement.txt
```

# Running

To start the server, make sure your venv is activated, then run this command:

```bash
uvicorn cities.main:app
```

While developing you might want to set the ``--reload`` option.

```
uvicorn cities.main:app --reload
```

No the REST server is up and running, but does not contain any data.
To add data, cd to the ``bin`` directory and then run the python 
script ``python populate_db.py``.

You can always reset the database by re-running this script (and 
optionally delete the ``cities.db`` file before). 

Now you can examine the API by opening this url in your browser:

http://localhost:8000/docs



