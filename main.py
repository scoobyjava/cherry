from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Cherry is online and ready!"}

@app.post("/generate-code/")
async def generate_code(task: str):
    """Cherry writes a script to accomplish the given task."""
    script = f"echo 'Executing Task: {task}'"
    return {"generated_script": script}

@app.post("/execute-code/")
async def execute_code(script: str):
    """Cherry executes a generated script."""
    with open("script.sh", "w") as f:
        f.write(script)
    subprocess.run(["bash", "script.sh"])
    return {"status": "Executed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
