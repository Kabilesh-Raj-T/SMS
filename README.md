# Store Management System (Python + MySQL)

A complete **Store Management System** built using **Python**, **MySQL**, for managing **products**, **customers**, **employees**, **sales**, **profits**, and **statistics**.  


---

## 🚀 Features

### 🛒 Product Management
- View product database
- Add new products or update stock
- Edit existing product details
- Delete products
- Search products by ID
- Record purchases and update stock automatically

### 👥 Customer Management
- View customer database
- Add new customers
- Edit customer details
- Delete customers
- Search customers by ID
- Maintain purchase history

### 🧑‍💼 Employee Management
- View employee database
- Add employees
- Edit employee details
- Delete employees
- Search employees by ID

### 📊 Finance & Statistics
- Calculate profit/loss for each product
- Calculate total store profit/loss
- Show best-selling products
- Show most profitable products

---

## 🛠️ Tech Stack
- **Python 3**
- **MySQL** (Database)
- **mysql-connector-python** (Python-MySQL connection)

---

## 📂 Project Structure
## ⚙️ Setup & Installation

### 1️⃣ Install Requirements
Make sure you have **Python 3** and **MySQL** installed.  
Then install the required Python package:
```bash
pip install mysql-connector-python

Step 1: Create the Database
Navigate to the setup folder:

bash
Copy code
cd setup
Log in to MySQL:

bash
Copy code
mysql -u root -p
Run the SQL file to create the database and tables:

sql
Copy code
source database_setup.sql;
(Replace database_setup.sql with the actual file name in the setup folder)

Exit MySQL:

sql
Copy code
exit;
Step 2: Run the Application
From the project root directory, run:

bash
Copy code
python -m src.main
