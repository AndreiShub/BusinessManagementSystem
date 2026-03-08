Business Management System

Business Management System is a backend application designed to help manage business operations such as tasks, teams, and user interactions.
The project exposes a REST API that allows users to create, update, and manage business entities in a structured way.

The system is built using Python and the modern web framework FastAPI, which provides high-performance APIs with automatic documentation and strong typing support.

This project demonstrates backend development practices including API design, authentication, database management, and automated testing.

Features

- User authentication and authorization
- Task management (create, update, delete, list)
- Team and user assignment to tasks

- RESTful API endpoints
- Database migrations
- Automated tests using pytest
- Modular and scalable project structure

Tech Stack

Backend:
- Python
- FastAPI
- SQLAlchemy
-Alembic

Database:
- PostgreSQL

Authentication:
-JWT authentication

Testing:
- pytest
  
Other Tools:
-Docker (optional)
-Git and GitHub

Main directories:

app/ – application source code
api/ – API endpoints
models/ – database models
schemas/ – Pydantic schemas
services/ – business logic
tests/ – automated tests

Installation:
Clone the repository:
git clone https://github.com/AndreiShub/BusinessManagementSystem.git
cd BusinessManagementSystem

Create a virtual environment:
python -m venv venv
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Environment Variables
Create a .env file and configure the following variables:
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
SECRET_KEY=your_secret_key

Database Migration

Run migrations using Alembic:
alembic upgrade head
Running the Application

Start the development server:
uvicorn app.main:app --reload

API will be available at:
http://localhost:8000

Interactive API documentation:
http://localhost:8000/docs


To run automated tests:
pytest

API Documentation:
FastAPI automatically generates interactive documentation.

Available endpoints documentation:
/docs or /redoc

Future Improvements
Role based access control
Notifications system
Advanced filtering and search
Frontend dashboard

Background tasks and scheduling

License

This project is licensed under the MIT License.
