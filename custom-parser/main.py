from typing import Union

from fastapi import FastAPI

app = FastAPI()

# mock api that provides dummy data
@app.get("/")
def read_root():
    return {
        "response" : [{
            "choices":[
                {
                "text" : "Custom",
                "index" : "0"
                },
            ]},
            {
            "choices":[
                {
                "text" : " Model",
                "index" : "1"
                },
            ]}]
    }
