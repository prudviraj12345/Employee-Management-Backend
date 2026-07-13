# Employee Management Backend - API Reference

## Run Server

```bash
python manage.py runserver
```

---

# Department Module

## Get All Departments

GET

http://127.0.0.1:8000/api/departments/

---

## Create Department

POST

http://127.0.0.1:8000/api/departments/

Example:

Department Name:
Human Resources

Description:
Handles employee recruitment and management.

---

## Update Department

PUT

http://127.0.0.1:8000/api/departments/1/

(Change 1 to the Department ID)

---

## Delete Department

DELETE

http://127.0.0.1:8000/api/departments/1/

---

# Employee Module

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

# Email Service

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

## View Emails

GET

http://127.0.0.1:8000/api/emails/

---

# History Module

## View Email History

GET

http://127.0.0.1:8000/api/history/

Shows:

- Employee
- Recipient Email
- Subject
- Message
- Status
- Retry Count
- Sent Time

---

# Demo Flow

1. Run Server

python manage.py runserver

2. Department CRUD

3. Employee CRUD

4. Email Service

5. History