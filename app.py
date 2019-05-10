'''
app.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This file contains the flask application in which our project runs.
To run the project, type in 'python app.py' in the terminal.
'''

from flask import (Flask, url_for, render_template, request, redirect, flash, session, jsonify)
import  incidentReporter, sys, json

app = Flask(__name__)
app.secret_key = 'secretkey123'


'''
home() route renders home page and login box, if necessary
'''
@app.route('/')
def home():
    try:
        uid = session['UID']
        print(uid)
    except:
        uid = None
    conn = incidentReporter.getConn('c9')   
    if uid:
        userInfo = incidentReporter.getUserInformation(conn, uid)
        return render_template('home.html',
                                userID = uid, 
                                userInfo = userInfo)
    else:
        userInfo = None
        return render_template('home.html', userID=uid, userInfo=userInfo)
       
'''
setUID() is a login route that
- Checks to make sure that credentials are submitted (not blank)
- Checks that provided email is a wellesley email
- Checks that B-number and email match one user
- Then sets user session and re-renders home page 
'''       
@app.route('/setUID/', methods=['POST'])
def setUID():
    if request.method == 'POST':
        print(request.form)
        
        uid = request.form.get('user_id')
        # User attempts to log in without any credentials
        if uid == '': 
            return redirect(url_for('home'))
            
        email = request.form.get('email')
        email_site = email.split("@")[1]
        # User attempts to log in with non-Wellesley email
        if email_site != 'wellesley.edu':
            flash('Error: please use Wellesley email credentials.')
            return redirect(url_for('home'))
            
        # Try to log in with email and B-number
        # Do that here
            
        session['UID'] = uid
        conn = incidentReporter.getConn('c9')   
        userInfo = incidentReporter.getUserInformation(conn, uid)
        return render_template('home.html', userID=uid, userInfo=userInfo)

'''
logout() route 
- Pops uid from session
- Redirects to home page
'''       
@app.route('/logout/')
def logout():
    session.pop('UID', None)
    return redirect(url_for('home'))
        
'''
incidentDetailPage(id) shows one incident in detail based on incident ID
'''            
@app.route('/incidentDetailPage/<id>')
def incidentDetailPage(id):
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    incidentInfo = incidentReporter.getIncidentInfo(conn, id)
    return render_template('incidentDetailPage.html', userInfo=userInfo, userID=uid, incident=incidentInfo)
    
'''
deleteIncident(id) deletes incident 
- 
'''        
@app.route('/deleteIncident/<id>')
def deleteIncident(id):
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    incidentReporter.deleteIncident(conn, id)
    return render_template('home.html', userInfo=userInfo, userID=uid)
    
'''
incidentReport() houses the main incident report form for students
- On GET, displays form
- On POST, submits incident report
'''    
@app.route('/incidentReport', methods=['POST', 'GET'])
def incidentReport():
    conn = incidentReporter.getConn('c9')
    uid = session['UID']
    if request.method == 'GET':
        userInfo = incidentReporter.getUserInformation(conn, uid)
        return render_template('incidentReport.html', userID = uid, 
                                userInfo = userInfo)
    else:
        rName = request.form['rname']
        aName = request.form['advocate']
        rID = incidentReporter.getIDFromName(conn, rName)
        aID = incidentReporter.getIDFromName(conn, aName)
        
        # a person cannot report themselves
        if uid == rID:
            flash('Error: you cannot report yourself')
            return redirect(request.referrer)
        # update database with information from a valid report
        info = request.form
        incidentReporter.insertIncident(conn, info, uid, rID, aID)
        return redirect(url_for('studentInbox'))

'''
studentInbox() displays all incidents reported by student
'''    
@app.route('/studentInbox/')
def studentInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedStudent(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
    
'''
facstaffInbox() displays all incidents reports in which the facstaff is reported 
'''     
@app.route('/facstaffInbox/')
def facstaffInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedFacstaff(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
'''
advocateInbox() displays all incidents reports in which 
the facstaff named an advocate
'''     
@app.route('/advocateInbox/')
def advocateInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedAdvocate(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

'''
adminInbox() displays all reported incidents
'''     
@app.route('/adminInbox/')
def adminInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllIncidents(conn)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
