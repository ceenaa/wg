import db

connection = db.connect()

db.create_table(connection)
db.load_all_peers(connection)
db.load_last_records(connection)

connection.commit()
connection.close()
