'''
app.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This file contains the flask application in which our project runs.
To run the project, type in 'python app.py' in the terminal.
'''

from flask import (Flask, url_for, render_template, request, redirect, flash, session, jsonify, Response)
import sys, json, incidentReporter, imghdr, datetime
from werkzeug import secure_filename

app = Flask(__name__)
app.secret_key = 'secretkey123'


'''
home() route renders home page and login box, if necessary
'''
@app.route('/')
def home():
    uid=session.get('UID')
    if uid:
        conn = incidentReporter.getConn('c9')
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
        conn = incidentReporter.getConn('c9')   
        userInfo = incidentReporter.getUserInformationWithEmail(conn, uid, email)
        if userInfo == None: 
            flash('Error: Invalid credentials.')
            return redirect(url_for('home')) 
        else: 
            session['UID'] = uid
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
deleteIncident(id) deletes incident report
- Only original reporter can delete an incident report
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
        facStaff = incidentReporter.getFacStaff(conn)
        return render_template('incidentReport.html', 
                                userID = uid, 
                                facStaff = facStaff,
                                userInfo = userInfo)
    else:
        rID = request.form['faculty']
        aID = request.form['advocate']
        
        # a person cannot report themselves
        if uid == rID:
            flash('Error: you cannot report yourself')
            return redirect(request.referrer)
        # update database with information from a valid report
        info = request.form
        
        # If user didn't upload a file, send last param as None
        if 'file' not in request.files:
            incidentReporter.insertIncident(conn, info, uid, rID, aID, None)
            return redirect(url_for('studentInbox'))
        else: 
            # get uploaded file 
            f = request.files['file']
            mime_type = imghdr.what(f.stream)
            if mime_type not in ['jpeg','gif','png', 'pdf']:
                raise Exception('Not a JPEG, GIF, PNG, or PDF: {}'.format(mime_type))
            upload = f.read()
            incidentReporter.insertIncident(conn, info, uid, rID, aID, upload)
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
    print(incidentsList)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
    
'''
facstaffInbox() displays all incidents reports in which the facstaff is reported 
'''     
@app.route('/facstaffInbox/')
def facstaffInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllReportedFacstaff(conn, uid)
    print(incidentsList)
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
    # print(incidentsList)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)
    
'''
adminInbox() displays all reported incidents (for admin)
'''     
@app.route('/adminInbox/')
def adminInbox():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentsList = incidentReporter.getAllIncidentsInbox(conn)
    userInfo = incidentReporter.getUserInformation(conn, uid)
    return render_template('inbox.html', userInfo=userInfo, userID=uid, incidentsList=incidentsList)

'''
'''
@app.route('/attachment/<reportID>')
def attachment(reportID):
    conn = incidentReporter.getConn('c9')   
    attachment = incidentReporter.getAttachment(conn, reportID)
    file = attachment['file']
    return Response(file, mimetype='attachment/'+imghdr.what(None,file))
    
    
'''
getMetrics helps to refresh the aggregate page
'''            
@app.route('/getMetrics')
def getMetrics():
    numIncidentsThisWeek, incidentByReported, incidentByLocation, incidentByCategory = getAggregateDataMetrics()
    return jsonify({"numIncidentsThisWeek": numIncidentsThisWeek, "incidentByReported": incidentByReported,
            "incidentByLocation": incidentByLocation, "incidentByCategory": incidentByCategory})

                            
'''
aggregate shows the admin the data in helpful aggregated forms
'''            
@app.route('/aggregate')
def aggregate():
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userInfo = incidentReporter.getUserInformation(conn, uid)
    
    numIncidentsThisWeek, incidentByReported, incidentByLocation, incidentByCategory = getAggregateDataMetrics()
    
    return render_template('aggregate.html', 
                            userInfo=userInfo, 
                            userID=uid,
                            numWeek=numIncidentsThisWeek,
                            reportedCounts=incidentByReported,
                            locationCounts=incidentByLocation,
                            categoryCounts=incidentByCategory)
'''
getAggregateDataMetrics is a helper function that abstracts the data analysis away from the routes
''' 
def getAggregateDataMetrics():
    conn = incidentReporter.getConn('c9')   
    incidentInfo = incidentReporter.getAllIncidentsAggregate(conn)

    numIncidentsThisWeek = getNumIncidentsThisWeek(incidentInfo)
    incidentByReported = getIncidentsThisReported(incidentInfo)
    incidentByLocation = getIncidentByLocation(incidentInfo)
    incidentByCategory = getIncidentByCategory(incidentInfo)
    
    return numIncidentsThisWeek, incidentByReported, incidentByLocation, incidentByCategory
    
def getNumIncidentsThisWeek(incidentInfo):
    result = 0
    for incident in incidentInfo:
        if (incident['dateOfIncident'] + datetime.timedelta(days=7) >= datetime.datetime.now().date()):
            result += 1
    return result

def getIncidentsThisReported(incidentInfo):
    result = {}
    for incident in incidentInfo:
        reported = incident['reportedName']
        if reported in result.keys():
            temp = result[reported]
            temp += 1
            result[reported] = temp
        else:
            result[reported] = 1
    return result

def getIncidentByLocation(incidentInfo):
    result = {}
    for incident in incidentInfo:
        location = incident['location'].lower().replace(" ", "")
        if location in result.keys():
            temp = result[location]
            temp += 1
            result[location] = temp
        else:
            result[location] = 1
    return result

def getIncidentByCategory(incidentInfo):
    result = {}
    for incident in incidentInfo:
        category = incident['category']
        if category in result.keys():
            temp = result[category]
            temp += 1
            result[category] = temp
        else:
            result[category] = 1
    return result


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
