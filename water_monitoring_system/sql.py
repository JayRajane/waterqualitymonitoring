from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT * FROM WaterQualityData")  # Replace with your table name
rows = cursor.fetchall()
print(rows)
