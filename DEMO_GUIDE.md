# Employee Management Backend - Demo Guide

## 1. Activate Virtual Environment

```bash
venv\Scripts\activate
```

---

## 2. Run Server

```bash
python manage.py runserver
```

---

# ADMIN LOGIN

## Create Superuser (Only Once)

```bash
python manage.py createsuperuser
```

Example

Username:
admin

Email:
admin@gmail.com

Password:
admin123

---

## Django Admin Panel

Open:

http://127.0.0.1:8000/admin/

Login with

Username:
admin

Password:
admin123

---

## Authentication API

Open:

http://127.0.0.1:8000/api/login/

POST

```json
{
    "username": "admin",
    "password": "admin123"
}
```

Expected Response

```json
{
    "success": true,
    "message": "Login Successful"
}
```

---

# DEPARTMENT MODULE

## Get All Departments

GET

http://127.0.0.1:8000/api/departments/

---

## Create Department

POST

http://127.0.0.1:8000/api/departments/

Example

Department Name:
Human Resources

Description:
Handles employee recruitment and management.

---

## Update Department

PUT

http://127.0.0.1:8000/api/departments/1/

(Change 1 to Department ID)

---

## Delete Department

DELETE

http://127.0.0.1:8000/api/departments/1/

---

# EMPLOYEE MODULE

## Get All Employees

GET

http://127.0.0.1:8000/api/employees/

---

## Create Employee

POST

http://127.0.0.1:8000/api/employees/

Example

Employee ID:
EMP101

First Name:
Rahul

Last Name:
Sharma

Email:
rahul@gmail.com

Phone:
9876543210

Department:
IT

Designation:
Software Engineer

---

## Update Employee

PUT

http://127.0.0.1:8000/api/employees/1/

(Change 1 to Employee ID)

---

## Delete Employee

DELETE

http://127.0.0.1:8000/api/employees/1/

---

# EMAIL SERVICE

## Get All Emails

GET

http://127.0.0.1:8000/api/emails/

---

## Create Email

POST

http://127.0.0.1:8000/api/emails/

Example

Recipient Email:
rahul@gmail.com

Subject:
Welcome Email

Message:
Welcome to ABC Company

Employee:
Rahul

Status:
Automatically becomes Sent

---

# HISTORY MODULE

## Get Email History

GET

http://127.0.0.1:8000/api/history/

Shows

- Employee
- Recipient Email
- Subject
- Message
- Status
- Retry Count
- Sent Time

---

# GITHUB

Check Status

```bash
git status
```

Add Files

```bash
git add .
```

Commit

```bash
git commit -m "Completed Employee Management Backend"
```

Push

```bash
git push origin main
```

---

# PROJECT MODULES

✔ Authentication

✔ Department

✔ Employee

✔ Email Service

✔ History

---

# DEMO FLOW

1. Run Server

```bash
python manage.py runserver
```

2. Authentication Login

3. Department CRUD

4. Employee CRUD

5. Email Service

6. History

7. Django Admin Panel
