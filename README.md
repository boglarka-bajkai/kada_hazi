# Interview Task: RESTful API for Task Management
A simple API made in Python FastApi for an interview. The recommendation endpoint uses a local tinyllama LLM. Both the API and the LLM are containerized.
## Setup instructions
- The API can be run in WSL with Docker Desktop connected, or any other environment with Docker support.
- To start the API service, run the following command: ```docker compose up --build```.
- This will start an ollama container for the task recommendation endpoint, and as soon as the model (tinyllama) is pulled, it will automatically start the API service. This might take some time the first time running the services, but will cache the model for subsequent startups.
- After the API service has started, it can be viewed and tested using Swagger at ```http://localhost:8000/docs```.
## Endpoint documentation
- /tasks
    - GET (without parameters): lists all tasks
    - GET additional parameters:
        - status: filters by status
        - due_date: filters by due date
        - sort_by: sorts by either creation date or due date
        - descending: sort order
    - POST: create new task
- /tasks/{id}
    - GET: get specific task by id
    - PUT: update full task by id
    - PATCH: update task partially by id
    - DELETE: delete task by id
- /smart
    - GET: returns the recommended title based on the last 5 titles
## Examples on how to use
- /tasks GET response body example:
```
[
  {
    "id": 1,
    "title": "Homework",
    "desc": "Programming homework.",
    "creation_date": "2025-06-10",
    "due_date": "2025-06-11",
    "status": "IN PROGRESS"
  },
  {
    "id": 2,
    "title": "Interview",
    "desc": "Programming interview.",
    "creation_date": "2025-06-11",
    "due_date": "2025-06-20",
    "status": "PENDING"
  },
  {
    "id": 3,
    "title": "Groceries",
    "desc": "Don't forget the milk.",
    "creation_date": "2025-06-11",
    "due_date": "2025-06-20",
    "status": "IN PROGRESS"
  },
  {
    "id": 4,
    "title": "Project meeting",
    "desc": "Check notes before the meeting.",
    "creation_date": "2025-06-11",
    "due_date": "2025-06-20",
    "status": "COMPLETED"
  },
  {
    "id": 5,
    "title": "Drawing",
    "desc": "Relax a bit.",
    "creation_date": "2025-06-11",
    "due_date": "2025-06-20",
    "status": "COMPLETED"
  }
]
```
- /tasks/{id} PATCH*, PUT and /tasks PUT request body:
```
{
  "title": "title",
  "desc": "description",
  "creation_date": "2025-06-10",
  "due_date": "2025-06-10",
  "status": "PENDING"
}
```
*: not all fields have to be present for PATCH

The detailed API documentation can be seen using Swagger, at ```http://localhost:8000/docs```
