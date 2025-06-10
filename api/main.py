import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from enum import Enum

import requests 

app = FastAPI()
DATABASE_NAME = "tasks.db"

class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETED = "COMPLETED"

class SortBy(str, Enum):
    CREATION_DATE = "creation_date"
    DUE_DATE = "due_date"

class TaskModelIn(BaseModel):
    title: str
    desc: str
    creation_date: date
    due_date: date
    status: Status

class TaskModelPatch(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    creation_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[Status] = None

class TaskModelOut(BaseModel):
    id: int
    title: str
    desc: str
    creation_date: date
    due_date: date
    status: Status

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        desc TEXT NOT NULL,
        creation_date DATE NOT NULL,
        due_date DATE NOT NULL,
        status TEXT NOT NULL       
    )
    """)
    # mock data
    curr_date = date.today()
    due_date = date.today() + timedelta(days=1)
    cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            ("Homework", "Programming homework.", curr_date, due_date, Status.IN_PROGRESS))
    curr_date = date.today() + timedelta(days=1)
    due_date = date.today() + timedelta(days=10)
    cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            ("Interview", "Programming interview.", curr_date, due_date, Status.PENDING))
    cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            ("Groceries", "Don't forget the milk.", curr_date, due_date, Status.IN_PROGRESS))
    cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            ("Project meeting", "Check notes before the meeting.", curr_date, due_date, Status.COMPLETED))
    cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            ("Drawing", "Relax a bit.", curr_date, due_date, Status.COMPLETED))
    conn.commit()
    conn.close()

#get-all (tasks)
@app.get("/tasks", response_model=list[TaskModelOut])
async def getTasks(status: Optional[Status] = None,
                    due_date: Optional[date] = None,
                    sort_by: Optional[SortBy] = None,
                    descending: bool = False) -> list[TaskModelOut]:
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM tasks"
        filters = []
        params = []

        if status:
            filters.append("status = ?")
            params.append(status.value)

        if due_date:
            filters.append("due_date = ?")
            params.append(due_date)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        if sort_by:
            query += f" ORDER BY {sort_by}"
            if descending:
                query += " DESC"

        tasks = cursor.execute(query, params).fetchall()
        return [dict(row) for row in tasks]

#get-specific (tasks/id)
@app.get("/tasks/{id}", response_model=TaskModelOut)
async def getTaskById(id: int) -> TaskModelOut:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return task

#post (create new)
@app.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=str)
async def createTask(task: TaskModelIn) -> str:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks
            (title, desc, creation_date, due_date, status)
            VALUES (?, ?, ?, ?, ?)""",
            (task.title, task.desc, task.creation_date, task.due_date, task.status.value))
    return "Created successfully"

#put (update tasks/id, replacing full)
@app.put("/tasks/{id}", response_model=str)
async def putTask(id: int, task: TaskModelIn) -> str:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        old_task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        if old_task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        cursor.execute("""
            UPDATE tasks SET
                title = ?,
                desc = ?,
                creation_date = ?,
                due_date = ?,
                status = ?
            WHERE id = ?""",
            (task.title, task.desc, task.creation_date, task.due_date, task.status, id)
        )
    return "Updated successfully"

#patch (update tasks/id, replacing only non-null)
@app.patch("/tasks/{id}", response_model=str)
async def patchTask(id: int, task: TaskModelPatch) -> str:
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        old_task = TaskModelOut(**dict(row))
        print(old_task)
        if old_task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        cursor.execute("""
            UPDATE tasks SET
                title = ?,
                desc = ?,
                creation_date = ?,
                due_date = ?,
                status = ?
            WHERE id = ?""",
            (task.title or old_task.title,
            task.desc or old_task.desc,
            task.creation_date or old_task.creation_date,
            task.due_date or old_task.due_date,
            task.status or old_task.status,
            id)
        )
    return "Updated successfully"

#delete (delete tasks/id)
@app.delete("/tasks/{id}")
async def deleteTask(id: int):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        task = cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
        if task is None:
            raise HTTPException(status_code=404, detail="The task does not exist, therefore it cannot be deleted.")
        cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
        return "Deleted successfully"

#smart endpoint
@app.get("/smart")
def getRecommendation() -> str:
    prompt = "Suggest what my next task title should be based on my previous tasks. Only reply with the task title, with no lead, at most 6 words. Previous tasks:"
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT title FROM tasks ORDER BY creation_date DESC LIMIT 5").fetchall()
        task_titles = [row[0] for row in rows]
        prompt += ", ".join(task_titles)
        prompt += ". Please suggest a title for my next task based on these titles."
    res = requests.post(
        f"http://ollama:11434/api/generate",
        json={"model": "tinyllama", "prompt": prompt, "stream": False},
        timeout=30
    )

    return res.json()["response"].strip()

@app.on_event("startup")
def startup_event():
    init_db()