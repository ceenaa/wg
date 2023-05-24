import db


connection = db.connect()

db.create_table(connection)
db.load_all_peers(connection)
db.load_lastRecords(connection)

connection.commit()
connection.close()