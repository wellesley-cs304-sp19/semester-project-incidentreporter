'''
testData.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This is a python file to create a JSON file of test data that we can use to insert
into our SQL database more efficiently.
'''

import json



data = {}  

# list of unencrypted passwords
passwords = ['']
data['users'] = [] 

for password in passwords:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    data['users'].append({
        'hashed': hashed
    })


data['users'].append({
    'name': name
    'email': email
    'hashed': hashed,
    'isAdmin': false,
    'role': role
})


with open('data.txt', 'w') as outfile:  
    json.dump(data, outfile)