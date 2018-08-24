# StormBot-Rewrite
Updated version of StormBot. Running the latest Discord.py

# Using SQL Class
The SQL Class uses the pyodbc library
Import class using:

`from odbc.mssql import *`

## Instantiate the SQL class and Usage
```
_sql = mssql()
id = 123456
cur = mssql.select(_sql, "select * from {tableName} where Id = ?", id)
rows = cur.fetchall()
for row in rows:
  # do something with the cursor
  ```
