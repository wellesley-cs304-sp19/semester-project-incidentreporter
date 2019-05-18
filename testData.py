'''
testData.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This is a python file to read a JSON file of test data that we can insert
into our SQL database more efficiently.
'''

import json, incidentReporter, bcrypt

with open('testData.json', 'r') as f:
    users = json.load(f)

# for each object in the parsed JSON file we hash the user's password and 
# then add that and all their information (name, email, administrative status, role) into
# our database using the insertNewUser function from incidentReporter.py
for user in users:
    hashed = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
    name = user['name']
    email = user['email']
    isAdmin = user['adminStatus']
    role = user['role']
    conn = incidentReporter.getConn('c9') 
    incidentReporter.insertNewUser(conn, hashed, name, email, isAdmin, role)
