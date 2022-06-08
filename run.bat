:: avtivate venv and start the restexample server
@ECHO OFF 

call venv\Scripts\python.exe  venv\Scripts\uvicorn.exe cities.main:app
