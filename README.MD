# Employee Leave & Approval Management System

## Overview

The Employee Leave & Approval Management System is a backend REST API developed using **FastAPI**, **PostgreSQL**, and **Async SQLAlchemy**. The application automates the employee leave management process by allowing employees to apply for leave, managers to approve or reject requests, HR to monitor leave records, and administrators to manage the system.

The project follows a layered architecture consisting of Router, Service, Repository, and Database layers, making the code modular, scalable, and easy to maintain.

---

# Features

## Authentication

- JWT Authentication
- Secure Login
- Password Hashing
- Protected APIs
- Bearer Token Authentication

---

## User Roles

The system supports four roles:

- Admin
- HR
- Manager
- Employee

---

## Department Management

- Create Department
- View Departments
- Update Department
- Delete Department

---

## User Management

- Create Employee
- View Employees
- Update Employee
- Delete Employee
- Assign Manager
- Assign Department

---

## Leave Types

- Create Leave Type
- View Leave Types
- Update Leave Type
- Delete Leave Type

---

## Leave Requests

Employees can

- Apply Leave
- Cancel Leave
- View Their Leave Requests

Managers can

- Approve Leave
- Reject Leave

---

## Business Validations

- Prevent overlapping leave requests
- Only pending requests can be approved or rejected
- Track leave status
- Manager approval workflow
- Leave request validations

---

## Reports

### Employee Report

Displays

- Employee Details
- Total Leave Requests
- Paid Leave Used
- Paid Leave Remaining
- Leave Type Breakdown

---

### Department Report

Displays

- Department Name
- Total Employees
- Total Leave Requests
- Paid Leave Used

---

### Monthly Report

Displays

- Total Leave Requests
- Approved Requests
- Pending Requests
- Rejected Requests
- Cancelled Requests
- Paid Leave Used

---

## Filters

Reports support

- Department Filter
- Manager Filter
- Employee Filter
- Leave Status Filter
- Month Filter
- Year Filter

---

## Pagination

Pagination is implemented for

- Employee Reports
- Department Reports

---

## Role Based Access Control (RBAC)

### Admin

- Full System Access

### HR

- Manage Leave Types
- View Reports
- View Employees

### Manager

- Approve Leave Requests
- Reject Leave Requests
- View Employees Assigned to Them
- View Reports of Assigned Employees

### Employee

- Apply Leave
- Cancel Leave
- View Own Leave Requests
- View Own Reports

---

# Technology Stack

- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (Async)
- AsyncPG
- Alembic
- Pydantic v2
- JWT Authentication
- Uvicorn

---

# Project Structure

```
app
│
├── auth
├── common
├── db
├── departments
├── leave_requests
├── leave_types
├── reports
├── users
│
├── main.py
│
alembic
│
.env
requirements.txt
README.md
```

---

# Database Setup

## Step 1: Install PostgreSQL

Download PostgreSQL

https://www.postgresql.org/download/

Install PostgreSQL and remember

- Username
- Password
- Port (Default: 5432)

---

## Step 2: Create Database

Open pgAdmin or DBeaver.

Execute

```sql
CREATE DATABASE employee_leave;
```

---

## Step 3: Configure Environment Variables

Create a `.env` file in the project root.

Example

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/employee_leave

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Replace

- postgres → PostgreSQL username
- password → PostgreSQL password
- employee_leave → your database name

---

## Step 4: Install Dependencies

Create Virtual Environment

```bash
python -m venv .venv
```

Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install Packages

```bash
pip install -r requirements.txt
```

---

# Database Migration

Run Alembic migrations

```bash
alembic upgrade head
```

This creates the following tables

- departments
- users
- leave_types
- leave_requests

---

## Useful Alembic Commands

Create Migration

```bash
alembic revision --autogenerate -m "Migration Name"
```

Upgrade Database

```bash
alembic upgrade head
```

Rollback One Migration

```bash
alembic downgrade -1
```

Current Migration

```bash
alembic current
```

---

# Running the Application

Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

Application URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

OpenAPI Documentation

```
http://127.0.0.1:8000/openapi.json
```

---

# API Modules

## Authentication

- Login

---

## Departments

- Create Department
- Get Departments
- Update Department
- Delete Department

---

## Users

- Create User
- Get Users
- Update User
- Delete User

---

## Leave Types

- Create Leave Type
- Get Leave Types
- Update Leave Type
- Delete Leave Type

---

## Leave Requests

- Apply Leave
- Cancel Leave
- Get Leave Request
- Get Employee Leave Requests
- Approve Leave
- Reject Leave

---

## Reports

- Employee Reports
- Department Reports
- Monthly Reports

Supports

- Filtering
- Pagination
- Role Based Access Control

---

# Authentication

This project uses JWT Bearer Authentication.

After logging in, use the access token in the Authorization header.

Example

```
Authorization: Bearer <access_token>
```

---

# Database Tables

The application consists of the following tables

- Users
- Departments
- Leave Types
- Leave Requests

---




Project developed as part of a Backend Development internship/academic project using FastAPI, PostgreSQL, and Async SQLAlchemy.
