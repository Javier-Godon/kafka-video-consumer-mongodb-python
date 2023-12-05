import uvicorn
from fastapi import FastAPI

from configuration.configuration import get_data

app = FastAPI()

port = get_data()['server']['port']

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
