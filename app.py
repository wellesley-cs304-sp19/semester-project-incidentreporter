'''
app.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This file contains the flask application.
'''

from flask import (Flask, url_for, render_template, request, redirect, flash, session, jsonify)
import  incidentReporter, sys, json

app = Flask(__name__)
app.secret_key = 'secretkey123'


'''
Home route
'''
@app.route('/')
def home():
    try:
        uid = session['UID']
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
       
@app.route('/setUID/', methods=['POST'])
def setUID():
    if request.method == 'POST':
        uid = request.form.get('user_id')
        session['UID'] = uid
        
        conn = incidentReporter.getConn('c9')   
        userInfo = incidentReporter.getUserInformation(conn, uid)
        
        return render_template('home.html', userID=uid, userInfo=userInfo)


@app.route('/logout/')
def logout():
    session.pop('UID', None)
    return redirect(url_for('home'))
        
@app.route('/incidentDetailPage/<id>')
def incidentDetailPage(id):
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    incidentInfo = incidentReporter.getIncidentInfo(conn, id)
    return render_template('incidentDetailPage.html', userInfo=userInfo, userID=uid, incident=incidentInfo)
    
@app.route('/deleteIncident/<id>')
def deleteIncident(id):
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    incidentReporter.deleteIncident(conn, id)
    return render_template('home.html', userInfo=userInfo, userID=uid)
    
# This function 
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

@app.route('/studentInbox/')
def studentInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedStudent(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
    
    
@app.route('/facstaffInbox/')
def facstaffInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedFacstaff(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

@app.route('/advocateInbox/')
def advocateInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedAdvocate(conn, uid)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

    
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
