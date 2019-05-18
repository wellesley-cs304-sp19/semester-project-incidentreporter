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
    
        
def insertNewUser(conn, hashed, name, email, isAdmin, role):
    ''' inserts a new user with the given parameters into the database, 
    
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

    
def getFacStaff(conn):
    ''' This function executes a query to retrieve the name and ID of all faculty
        staff users. This function will be used in app.py to auto-populate a 
        form input.
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select name, BNUM from user where role = "facstaff"''')
    return curs.fetchall()
    
  
def insertIncident(conn, form, uid, rID, aID, attachment):
    '''
    This function creates an incident report with the information that is passed
    in as parameters and adds the report information to the database
    - Gets the most recent ID and calls uploadFile() with this reportID
    
    Parameters
    ----------
    form: the incident report form that is being filled out
    uid: user ID
    rID: ID of the person being reported
    aID: ID of advocate
    attachment: file that is being attached to report
    '''  
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
    '''
    This function allows the reporter to update an incident they have previously
    submitted.
    
    Parameters
    ----------
    reportID: the report ID that is being edited
    anonymousToReported: whether the user wants to remain anonymous to the person
                         they're reporting
    anonymousToAll: whether the person wants to remain anonymous to all
    advocateID: ID of the advocate
    reportedID: ID of the person who is being reportedID
    location: location of incident 
    date: date of incident
    category: type of incident 
    description: description of incident
    '''
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
    
   
def uploadFile(conn, attachment, reportID):
    '''
    This function is called in insertIncident() after a 
    report is created when a user uploads a file.
    
    Parameters
    ----------
    conn: databse connection
    attachment: the file attachment to the report
    reportID: report ID
    '''   
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into uploadblob(reportID, file) values (%s,%s)''', [reportID, attachment])
    conn.commit()


def getAttachment(conn, reportID):
    '''
    This function executes a query to select a file from a report based on a given
    report ID.
    
    Parameters
    ----------
    conn: databse connection
    reportID: report ID
    '''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select file from uploadblob where reportID = %s''', [reportID])
    return curs.fetchone()



def getAllReportedFacstaff(conn, BNUM):
    '''
    This function gets all incidents reported about a specific 
    facstaff user given their BNUM, and also the name of the student who reported
    the facstaff member.
    
    Parameters
    ----------
    conn: databse connection
    BNUM: faculty staff member user ID
    '''
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
    

def getAllReportedAdvocate(conn, BNUM):
    ''' 
    This function uses a faculty/staff's BNUM to get all incidents for which 
    they are an advocate, and also the name of the students who reported.
    
    Parameters
    ----------
    conn: databse connection
    BNUM: a faculty/staff's BNUM
    '''
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


def getAllReportedStudent(conn, BNUM):
    '''
    This function gets all incidents reported by a specific 
    student using their BNUM, and also the names of facstaff who were implicated
    in the report.
    
    Parameters
    ----------
    conn: databse connection
    BNUM: a student's BNUM
    '''
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
    ''' 
    This function gets all reported incident information from the database 
    for admin view 
    Parameters
    ----------
    conn: databse connection
    '''
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


def getAllIncidentsAggregate(conn):
    ''' 
    This function gets all reported incidents for admins to view as aggregate data
    Parameters
    ----------
    conn: databse connection
    '''
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


def getIncidentInfo(conn, id):
    '''
    This function gets one incident based on a given reportID
    Parameters
    ----------
    conn: databse connection
    id: report ID
    '''
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


def deleteIncident(conn, id):
    '''
    This function deletes one incident based on the given reportID
    Parameters
    ----------
    conn: databse connection
    id: report ID
    '''
    
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from incident where reportID = %s''', [id])
    conn.commit()

if __name__ == '__main__':
    conn = getConn('c9')
    # print(getAllReportedFacstaff(conn, 10000000))
    # print(getAllReportedStudent(conn, 1))
    # print(getAllIncidents(conn))
