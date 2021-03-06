'''
app.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This file contains the flask application in which our project runs.
To run the project, type in 'python app.py' in the terminal.
'''

from flask import (Flask, url_for, render_template, request, redirect, flash, session, jsonify, Response)
import sys, json, incidentReporter, imghdr, datetime, bcrypt, MySQLdb, os
from werkzeug import secure_filename
from threading import Lock

app = Flask(__name__)
app.secret_key = 'secretkey123'

@app.route('/')
def home():
    ''' Home route renders home page, navigation bar, and login box, if necessary. 
    '''
    uid=session.get('UID')
    userType = session.get('role')
    admin = session.get('admin')
    return render_template('home.html', userID = uid, userType=userType, admin=admin, page_title="home")

        
@app.route('/join/', methods=["POST"])
def join():
    ''' Join route for a user to create an account in our database. 
        Additionally, performs the following:
        - checks that passwords entered match each other
        - stores hashed version of user's password with salt for security purposes 
        - ensures the entered email doesn't already exist in our database
        - stores name, email, BNUM, login status, admin status, and user role in session  
        
        Users are unable to create an account with admin status in order to 
        prevent just anyone from gaining administrative rights
        
        Finally, redirects to home route.
        
        Any potential errors are flashed. 
    '''
    try:
        name = request.form.get('name')
        email = request.form.get('email-j')
        userType = request.form.get('userType')
        passwd1 = request.form.get('password1')
        passwd2 = request.form.get('password2')
        if passwd1 != passwd2:
            flash('passwords do not match')
            return redirect( url_for('home'))
        hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
        
        conn = incidentReporter.getConn('c9') 
        curs = conn.cursor()
        try: 
            incidentReporter.insertNewUser(conn, hashed, name, email, False, userType)
        except MySQLdb.IntegrityError as err:
            flash('That email is already in the system')
            return redirect(url_for('home'))
        curs.execute('select last_insert_id()')
        row = curs.fetchone()
        uid = row[0]
        session['name'] = name
        session['email'] = email
        session['UID'] = uid
        session['logged_in'] = True
        session['role'] = userType
        session['admin'] = False
        return redirect( url_for('home', userID=uid, userType=userType, admin=False))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('home') )
        
@app.route('/login/', methods=["POST"])
def login():
    ''' Login route for users with existing accounts to log in. 
        Additionally, performs the following:
        - checks if entered password matches the one that is associated with the 
          user's email/info
        - flashes error if user enters incorrect password or an email that is not
          yet in the system
        - stores name, email, BNUM, login status, admin status, and user role in session  
        
        Finally, redirects to home page.
        
        Any potential errors are flashed.
    '''
    try:
        email = request.form.get('email')
        passwd = request.form.get('password')
        conn = incidentReporter.getConn('c9')
        curs = conn.cursor(MySQLdb.cursors.DictCursor)
        curs.execute('SELECT BNUM,hashed,name,isAdmin,role FROM user WHERE email = %s',
                     [email])
        person = curs.fetchone()
        if person is None:
            # Same response as wrong password, so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
        hashed = person['hashed']
        # strings always come out of the database as unicode objects
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            session['name'] = person['name']
            session['email'] = email
            session['UID'] = person['BNUM']
            session['logged_in'] = True
            session['admin'] = person['isAdmin']
            session['role'] = person['role']
            return redirect( url_for('home'))
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
    except Exception as err:
        print('form submission error '+str(err))
        return redirect(url_for('home') )

     
@app.route('/logout/')
def logout():
    '''
    logout() route 
    - Pops all user information from session
    - Redirects to home page
    '''  
    try:
        if 'UID' in session:
            uid = session['UID']
            session.pop('name')
            session.pop('email')
            session.pop('UID')
            session.pop('logged_in')
            session.pop('admin')
            session.pop('role')
            
            flash('You are logged out')
            return redirect(url_for('home'))
        else:
            flash('You are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('home') )
        
@app.route('/incidentDetailPage/<id>')
def incidentDetailPage(id):
    '''This function shows takes one parameter, id, the incident ID and 
       renders the page with all details regarding the incident with the given ID.
    ''' 
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    admin = session.get('admin')
    incidentInfo = incidentReporter.getIncidentInfo(conn, id)
    return render_template('incidentDetailPage.html', userID=uid,admin=admin, userType=userType, incident=incidentInfo, page_title="detail page")
    
      
@app.route('/deleteIncident/<id>')
def deleteIncident(id):
    ''' This function takes an ID of an incident report as a parameter and 
        deletes the incident report associated with the given ID. 
        - Only the original reporter can delete an incident report
        - Renders home page
    '''  
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    incidentReporter.deleteIncident(conn, id)
    return render_template('home.html', userID=uid, page_title="home")


@app.route('/editDetailPage/<id>')
def editDetailPage(id):
    '''
    This function takes in one parameter, an incident report ID. This route
    leads to a page where students can edit the incidents they have already created
    -only students can edit reports
    -reports will be automatically saved via ajax
    '''
    #general set up
    conn = incidentReporter.getConn('c9')
    uid = session['UID']
    facStaff = incidentReporter.getFacStaff(conn)
    incidentInfo = incidentReporter.getIncidentInfo(conn, id)
    userType = session['role']
    #render the same template used to report an incident, but this time
    #submit is false (we are not submitting an incident) and incident Info has a value
    return render_template('incidentReport.html', 
                            userID = uid, 
                            facStaff = facStaff,
                            userType = userType,
                            submit=False,
                            incidentInfo=incidentInfo)

  
@app.route('/incidentReport', methods=['POST', 'GET'])
def incidentReport():
    '''
    incidentReport() houses the main incident report form for students
    - On GET, displays form
    - On POST, submits incident report
    '''  
    reportLock = Lock()
    reportLock.acquire()
    conn = incidentReporter.getConn('c9')
    uid = session['UID']
    userType = session['role']
    admin = session.get('admin')
    if request.method == 'GET':
        facStaff = incidentReporter.getFacStaff(conn)
        reportLock.release()
        return render_template('incidentReport.html', 
                                userID = uid, 
                                admin=admin,
                                userType=userType,
                                facStaff = facStaff,
                                submit=True,
                                incidentInfo=None,
                                page_title="incident report")
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
            return redirect(url_for('studentInbox', userType=userType, admin=admin, page_title="student inbox"))
        else: 
            # get uploaded file 
            f = request.files['file']
            mime_type = imghdr.what(f.stream)
            if mime_type not in ['jpeg','gif','png', 'pdf']:
                raise Exception('Not a JPEG, GIF, PNG, or PDF: {}'.format(mime_type))
            upload = f.read()
            incidentReporter.insertIncident(conn, info, uid, rID, aID, upload)
            reportLock.release()
            return redirect(url_for('studentInbox', userType=userType, admin=admin, page_title="student inbox"))

    
@app.route('/studentInbox/')
def studentInbox():
    '''
    This route renders the student inbox which displays all incidents reported by student
    '''
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    isAdmin = session['admin']
    incidentsList = incidentReporter.getAllReportedStudent(conn, uid)
    return render_template('inbox.html', userType=userType, 
                            isAdmin=isAdmin, userID=uid, 
                            incidentsList=incidentsList, page_title="student inbox")
    
@app.route('/updateIncident')
def updateIncident():
    '''
    updateIncident() is called by the ajax call to update the incident
    -reads all fields in the format
    -calls a function in the DAO to update the incident table
    -upon success, returns a success message to the front end
    ''' 
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    
    #get all the information from the fields on the front end
    reportID = request.args.get('reportID')
    anonymousToReported = request.args.get('anonymousToReported')
    anonymousToAll = request.args.get('anonymousToAll')
    advocateID = request.args.get('advocateID')
    reportedID = request.args.get('reportedID')
    location = request.args.get('location')
    date = request.args.get('date')
    category = request.args.get('category')
    description = request.args.get('description')
    
    #call to DAO 
    success = incidentReporter.updateIncident(conn, reportID, 
                                                    anonymousToReported, 
                                                    anonymousToAll, 
                                                    advocateID,
                                                    reportedID,
                                                    location,
                                                    date,
                                                    category,
                                                    description)
                               
    #return success message                                                 
    return jsonify({'success': success})
    
@app.route('/facstaffInbox/')
def facstaffInbox():
    '''
    This route renders the faculty/staff inbox which displays all incident reports 
    in which the facstaff is reported 
    ''' 
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    admin = session['admin']
    incidentsList = incidentReporter.getAllReportedFacstaff(conn, uid)
    return render_template('inbox.html', userType=userType, admin=admin, 
                            userID=uid, incidentsList=incidentsList, page_title="fac staff inbox")

@app.route('/advocateInbox/')
def advocateInbox():
    '''
    This route renders the advocate inbox which displays all incidents reports in which 
    the facstaff is named an advocate
    '''  
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    admin = session['admin']
    incidentsList = incidentReporter.getAllReportedAdvocate(conn, uid)
    return render_template('inbox.html', userType=userType, admin=admin, 
                            userID=uid, incidentsList=incidentsList, page_title="advocate inbox")
    
     
@app.route('/adminInbox/')
def adminInbox():
    '''
    This route renders the admin inbox which displays all reported incidents (for admin)
    '''
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    admin = session['admin']
    incidentsList = incidentReporter.getAllIncidentsInbox(conn)
    return render_template('inbox.html', userType=userType, admin=admin, 
                            userID=uid, incidentsList=incidentsList, page_title="admin inbox")

@app.route('/attachment/<reportID>')
def attachment(reportID):
    '''
    attachment(reportID) allows users to attach a file to their incidentDetailPage
    '''
    conn = incidentReporter.getConn('c9')   
    attachment = incidentReporter.getAttachment(conn, reportID)
    file = attachment['file']
    return Response(file, mimetype='attachment/'+imghdr.what(None,file))
    
           
@app.route('/aggregate')
def aggregate():
    '''
    aggregate shows the admin the data in helpful aggregated forms
    ''' 
    conn = incidentReporter.getConn('c9')   
    uid = session['UID']
    userType = session['role']
    admin = session['admin']
    
    #users helper function to get all metrics to pass to the front end
    numIncidentsThisWeek, incidentByReported, incidentByLocation, incidentByCategory = getAggregateDataMetrics()
    
    return render_template('aggregate.html',
                            userID=uid,
                            admin=admin,
                            userType=userType,
                            numWeek=numIncidentsThisWeek,
                            reportedCounts=incidentByReported,
                            locationCounts=incidentByLocation,
                            categoryCounts=incidentByCategory,
                            page_title="aggregate data")

def getAggregateDataMetrics():
    '''
    getAggregateDataMetrics is a helper function that abstracts the data analysis away from the route
    ''' 
    conn = incidentReporter.getConn('c9')   
    incidentInfo = incidentReporter.getAllIncidentsAggregate(conn)

    #call helper functions
    numIncidentsThisWeek = getNumIncidentsThisWeek(incidentInfo)
    incidentByReported = getIncidentsThisReported(incidentInfo)
    incidentByLocation = getIncidentByLocation(incidentInfo)
    incidentByCategory = getIncidentByCategory(incidentInfo)
    
    return numIncidentsThisWeek, incidentByReported, incidentByLocation, incidentByCategory
    
def getNumIncidentsThisWeek(incidentInfo):
    '''
    getNumIncidentsThisWeek is a helper function that loops through Incident Info to calculate meta data
    ''' 
    result = 0
    for incident in incidentInfo:
        if (incident['dateOfIncident'] + datetime.timedelta(days=7) >= datetime.datetime.now().date()):
            result += 1
    return result

def getIncidentsThisReported(incidentInfo):
    '''
    getIncidentsThisReported is a helper function that loops through Incident Info to calculate meta data
    '''
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
    '''
    getIncidentByLocation is a helper function that loops through Incident Info to calculate meta data
    '''
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
    '''
    getIncidentByCategory is a helper function that loops through Incident Info to calculate meta data
    '''
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
