import sqlite3
db=sqlite3.connect('twitterDB.db')
db.execute("CREATE TABLE tweets (id INTEGER PRIMARY KEY, tweetID VARCHAR(30) NOT NULL, tweet BLOB NOT NULL, archiveID INTEGER NOT NULL, position INTEGER NOT NULL)")
db.execute("CREATE TABLE archives (id INTEGER PRIMARY KEY, name VARCHAR(30) NOT NULL)")
db.execute("CREATE TABLE sharedArchive (id INTEGER PRIMARY KEY, ownerID INTEGER NOT NULL, sharedUserID INTEGER NOT NULL, sharedArchiveID INTEGER NOT NULL)")
db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR(30) NOT NULL, password VARCHAR(30) NOT NULL)")
db.execute("INSERT INTO archives (id, name) VALUES (?,?)", (1, 'General'))
db.execute("INSERT INTO users (name, password) VALUES (?,?)", ('stuart', 'password'))
db.commit()