'''
incidentReporter.py
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

This file contains the SQL queries to our database.
'''

import sys
import MySQLdb

ADDED_BY = 1341
    
def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    return conn
    
'''
getUserInformation(conn, userID) will get all of the information of the logged 
in user as it is in the database, using the BNUM (userID) 

*** MIGHT NOT NEED THIS ANYMORE SINCE EVERYTHING IS STORED IN SESSIONS?***
'''
def getUserInformation(conn, userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''select * from user where BNUM = %s''', [userID])
        return curs.fetchone()
    except:
        return None
        
        
	
def insertNewUser(conn, hashed, name, email, isAdmin, role):
    ''' inserts a new user with the given parameters into the database, also
        returns 
    
        Parameters
        ----------
        hashed: the hashed version of a user's password, with salt
        name: user's name
        email: user's email
        isAdmin: Boolean value that reflects whether the user is an admin
        role: user type, either facstaff or student
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    add = ('''insert into user  
           (hashed, name, email, isAdmin, role)
            values(%s,%s,%s,%s,%s)''')
    values = (hashed, name, email, isAdmin, role)
    curs.execute(add, values)
    conn.commit()
    
'''
getUserInformationWithEmail(conn, userID) will get all of the information of the logged 
in user as it is in the database, using the BNUM (userID) AND email
'''       
def getUserInformationWithEmail(conn, userID, email):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''select * from user where BNUM = %s and email = %s''', [userID, email])
        return curs.fetchone()
    except:
        return None        
        
def getBNUM(conn, email):
    ''' get the UID/BNUM of the user with the email provided. 
    
        Parameters
        ----------
        email: a user's email address they use to log in
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        curs.execute('''select BNUM from user where email = %s''', [email])
        return curs.fetchone()
    except:
        return None  


def getIDFromName(conn, name):
    ''' Gets the UID of the person who is being reported based on the given name 
    ***will not need this in the alpha version ideally because we will change 
    the incident reporting form so that this form element will be a drop down
    # menu with options of faculty rather than a free for all text box***
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select BNUM from user where name=%s''', [name])
    return curs.fetchall()
    
def getFacStaff(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select name, BNUM from user where role = "facstaff"''')
    return curs.fetchall()
    
'''
insertIncident(conn, form, uid, rID, aID) creates an incident report and 
adds it to the database
- Gets the most recent ID and calls insertBlob() with this reportID
'''    
def insertIncident(conn, form, uid, rID, aID, attachment):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    add = ("insert into incident " 
           "(reporterID,reportedID,advocateID,location,category,dateOfIncident,anonymousToAll,anonymousToReported,description)"
           "values(%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    values = (uid,rID,aID,
              form['location'],form['category'],form['date'],
              form['anon-all'],form['anon-r'],form['description'])
    curs.execute(add, values)
    conn.commit()
    
    # Only upload a blob if the user inputted a file
    if attachment is not None:
        reportID = curs.lastrowid
        uploadFile(conn, attachment, reportID)
    
    
def updateIncident(conn, reportID, 
                        anonymousToReported,
                        anonymousToAll,                            
                        advocateID,
                        reportedID,
                        location,
                        date,
                        category,
                        description):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    
    curs.execute('''UPDATE incident
                    SET anonymousToReported = %s,
                        anonymousToAll = %s,                           
                        advocateID = %s,
                        reportedID = %s,
                        location = %s,
                        dateOfIncident = %s,
                        category = %s,
                        description = %s
                    WHERE reportID = %s; ''', [anonymousToReported,
                                                anonymousToAll,                            
                                                advocateID,
                                                reportedID,
                                                location,
                                                date,
                                                category,
                                                description,
                                                reportID])
    conn.commit()
    return True
    
'''
insertBlob(conn, uploadBlob, reportID) is called in insertIncident() after a 
report is created when a user uploads a file
'''      
def uploadFile(conn, attachment, reportID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into uploadblob(reportID, file) values (%s,%s)''', [reportID, attachment])
    conn.commit()

'''
'''
def getAttachment(conn, reportID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select file from uploadblob where reportID = %s''', [reportID])
    return curs.fetchone()


'''
getAllReportedFacstaff(conn, BNUM) Gets all incidents reported about a specific 
facstaff user by their BNUM, and also the name of the student who reported
'''
def getAllReportedFacstaff(conn, BNUM):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select reportID as reportID,
                            dateOfIncident as dateOfIncident,
                            anonymousToReported as anonymousToReported,
                            anonymousToAll as anonymousToAll,
                            description as description,
                            reporterTab.name as reporterName,
                            advocateTab.name as advocateName,
                            reportedTab.name as reportedName
                            
                            from incident 
                        inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                        inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                        inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                        where reportedID=%s''', [BNUM])
    return curs.fetchall()
    
# Gets all incidents reported for which a facstaff is an advocate by their BNUM, and also the name of the students who reported
def getAllReportedAdvocate(conn, BNUM):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select reportID as reportID,
                                dateOfIncident as dateOfIncident,
                                anonymousToReported as anonymousToReported,
                                anonymousToAll as anonymousToAll,
                                reporterTab.name as reporterName,
                                advocateTab.name as advocateName,
                                reportedTab.name as reportedName,
                                incident.description as description
                                
                                from incident 
                            inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                            inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                            inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                            where advocateID=%s''', [BNUM])    
    return curs.fetchall()

'''
getAllReportedStudent(conn, BNUM) gets all incidents reported by a specific 
student using their BNUM, and also the names of facstaff who were implicated
in the report
***Do we need another inner join to get the advocate's name?***
'''
def getAllReportedStudent(conn, BNUM):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select incident.reportID as reportID,
                            dateOfIncident as dateOfIncident,
                            anonymousToReported as anonymousToReported,
                            anonymousToAll as anonymousToAll,
                            reporterTab.name as reporterName,
                            advocateTab.name as advocateName,
                            reportedTab.name as reportedName,
                            incident.description as description, 
                            attachment.file as file
                            
                            from incident 
                        inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                        inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                        inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                        left join uploadblob attachment on incident.reportID=attachment.reportID
                        where reporterID=%s''', [BNUM])
    return curs.fetchall()
    
    
def getAllIncidentsInbox(conn):
    ''' gets all reported incident information from the database for admin view '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select incident.reportID as reportID,
                            dateOfIncident as dateOfIncident,
                            anonymousToReported as anonymousToReported,
                            anonymousToAll as anonymousToAll,
                            reporterTab.name as reporterName,
                            advocateTab.name as advocateName,
                            reportedTab.name as reportedName,
                            incident.description as description,
                            attachment.file as file
                            
                            from incident 
                        inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                        inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                        inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                        left join uploadblob attachment on incident.reportID=attachment.reportID
                        ''')
    return curs.fetchall()

''' getAllIncidents(conn) gets all reported incidents for admins to view as aggregate data'''
def getAllIncidentsAggregate(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select dateOfIncident as dateOfIncident,
                            reportedTab.name as reportedName,
                            incident.location as location,
                            incident.category as category
                            
                            from incident 
                        inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                        inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                        inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                        ''')
    return curs.fetchall()

'''
This function gets one incident based on reportID
'''
def getIncidentInfo(conn, id):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select incident.reportID as reportID,
                            dateOfIncident as dateOfIncident,
                            anonymousToReported as anonymousToReported,
                            anonymousToAll as anonymousToAll,
                            reporterTab.name as reporterName,
                            advocateTab.name as advocateName,
                            reportedTab.name as reportedName,
                            incident.description as description,
                            incident.location as location,
                            incident.category as category,
                            incident.reporterID as reporterID,
                            incident.reportedID as reportedID,
                            incident.advocateID as advocateID,
                            attachment.file as file
                            
                            
                            from incident 
                        inner join user reporterTab on incident.reporterID=reporterTab.BNUM 
                        inner join user advocateTab on incident.advocateID=advocateTab.BNUM 
                        inner join user reportedTab on incident.reportedID=reportedTab.BNUM
                        left join uploadblob attachment on incident.reportID=attachment.reportID
                        where incident.reportID = %s
                        ''', [id])
    return curs.fetchone()

'''
This function deletes one incident based on reportID
'''
def deleteIncident(conn, id):
    print(id)
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from incident where reportID = %s''', [id])
    conn.commit()

if __name__ == '__main__':
    conn = getConn('c9')
    # print(getAllReportedFacstaff(conn, 10000000))
    # print(getAllReportedStudent(conn, 1))
    # print(getAllIncidents(conn))
