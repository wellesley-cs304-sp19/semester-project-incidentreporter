

from flask import (Flask, url_for, render_template, request, redirect, flash, session, jsonify)
import  incidentReporter, sys, json

app = Flask(__name__)
app.secret_key = 'secretkey123'

@app.route('/')
def home():
    try:
        uid = session['UID']
    except:
        uid = None
    conn = incidentReporter.getConn('c9')   
    if uid:
        print (uid)
        userInfo = incidentReporter.getUserInformation(conn, uid)
        print(userInfo)
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
        return redirect(url_for('home'))

@app.route('/incidentDetailPage/<id>')
def incidentDetailPage(id):
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    print(userInfo)
    incidentInfo = incidentReporter.getIncidentInfo(conn, id)
    print(incidentInfo)
    return render_template('incidentDetailPage.html', userInfo=userInfo, userID=uid, incident=incidentInfo)
    
    
@app.route('/studentInbox/')
def studentInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedStudent(conn, uid)
    print(incidentsList)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
    
    
@app.route('/facstaffInbox/')
def facstaffInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedFacstaff(conn, uid)
    print(incidentsList)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

    
@app.route('/adminInbox/')
def adminInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllIncidents(conn)
    print(incidentsList)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

          
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
