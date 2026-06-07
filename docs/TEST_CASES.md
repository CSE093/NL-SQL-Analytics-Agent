# NL to SQL Test Cases

This document lists example input/output cases for the `NL TO SQL` project. It is intended as a reference for expected behavior and functional coverage.

## 1. CSV / Excel Upload Sanitization

### Input
- Filename: `Sales_Data_2025.csv`
- Columns: `First Name`, `Age`, `City/Region`

### Expected Output
- Table name: `sales_data_2025`
- Column names: `first_name`, `age`, `city_region`
- Row count: same as input rows

---

### Input
- Filename: `123orders.csv`

### Expected Output
- Table name: `t_123orders`

---

### Input
- Filename: `Select.csv`

### Expected Output
- Table name: `t_select`

---

### Input
- Filename: `___orders___data___.csv`

### Expected Output
- Table name: `orders_data`

---

## 2. SQL Execution

### Input
- SQL: `SELECT * FROM sales`

### Expected Output
- A valid `pandas.DataFrame`
- Contains 3 rows for the sample sales table
- Contains columns: `item_id`, `item_name`, `price`

---

### Input
- SQL: `SELECT * FROM non_existent_table`

### Expected Output
- Execution raises an SQLite error or `pandas.errors.DatabaseError`

---

### Input
- SQL: `INSERT INTO sales (item_id, item_name, price) VALUES (4, 'Widget D', 15.0)` using the readonly connection

### Expected Output
- `sqlite3.OperationalError`
- Error message includes: `attempt to write a readonly database`

---

## 3. SQL Validation

### Input
- SQL: `SELECT * FROM customers`

### Expected Output
- `is_valid = True`
- `msg` indicates the query is allowed

---

### Input
- SQL: `SELECT name, (SELECT SUM(amount) FROM orders WHERE orders.customer_id = customers.id) FROM customers`

### Expected Output
- `is_valid = True`

---

### Input
- SQL: `WITH monthly_sales AS (SELECT customer_id, SUM(amount) as total FROM orders GROUP BY customer_id) SELECT * FROM monthly_sales JOIN customers ON customers.id = monthly_sales.customer_id`

### Expected Output
- `is_valid = True`

---

### Input
- SQL: `DROP TABLE customers`

### Expected Output
- `is_valid = False`
- `msg` contains `blocked` or `banned`

---

### Input
- SQL: `DELETE FROM orders WHERE id = 1`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `INSERT INTO customers (name) VALUES ('Hacker')`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `UPDATE orders SET amount = 0.0 WHERE customer_id = 1`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `ALTER TABLE customers ADD COLUMN hack TEXT`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `PRAGMA foreign_keys = OFF`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `ATTACH DATABASE 'test.db' AS test`

### Expected Output
- `is_valid = False`

---

### Input
- SQL: `SELECT * FROM customers /* DROP TABLE customers; */`

### Expected Output
- `is_valid = True`
- Comments are stripped before validation

---

## 4. Agent Flow / Natural Language to SQL

### Input
- Natural language: `Show customers in New York`

### Expected Output
- `success = True`
- Generated SQL: `SELECT * FROM customers WHERE city = 'New York';`
- `retry_count = 0`
- `data` contains 1 row
- `explanation` describes the query result

---

### Input
- Natural language: `Find customer named Alice`
- Simulate first generated SQL with a syntax error, then a corrected SQL on retry

### Expected Output
- `success = True`
- Generated SQL: `SELECT * FROM customers WHERE name = 'Alice';`
- `retry_count = 1`
- `errors` contains one execution or syntax error message
- `data` contains 1 row

---

## 5. Table Management

### Input
- Upload CSV: `table_to_delete.csv`
- Data: `name = Alpha`, `value = 1`

### Expected Output
- `table_name` is returned after ingestion
- `rows = 1`
- `table_name` appears in `list_user_tables()` after ingestion
- After `delete_user_table(table_name)`, the table is no longer listed

---

## Notes
- These cases are derived from the existing Pytest suite and project behavior.
- They represent the main functional flows: upload sanitization, SQL validation, safe query execution, and natural language agent retries.
