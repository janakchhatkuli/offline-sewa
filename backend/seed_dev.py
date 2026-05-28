import sqlite3
import os

db = r"c:\Users\janak\Desktop\offline-sewa\dev.db"
c = sqlite3.connect(db)
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("tables:", tables)

# Seed if empty
n = c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
if n == 0:
    c.execute("INSERT INTO customers (customer_id,name,phone,online_balance,offline_balance,is_active) VALUES (?,?,?,?,?,?)",
              ("cust_demo", "Demo Cust", "+9779800000001", 0, 500, 1))
    c.execute("INSERT INTO merchants (merchant_id,name,phone,pending_settlement,settled_balance,is_active) VALUES (?,?,?,?,?,?)",
              ("merch_demo", "Demo Merch", "+9779800000002", 0, 0, 1))
    c.commit()
    print("seeded demo customer + merchant")
else:
    print("customers already present:", n)
