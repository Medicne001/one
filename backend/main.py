from fastapi import FastAPI
import os
app = FastAPI(title="Backend placeholder")
@app.get("/")
def root():
    return {"status":"backend ok"}
