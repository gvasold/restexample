#! /bin/bash

## avticate venv and run the cities server on port 8080

source venv/bin/activate && uvicorn cities.main:app