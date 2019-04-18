import sys
import MySQLdb

ADDED_BY = 1341
    
def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    return conn
    

def getUserInformation(conn, userID):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    try:
        
        curs.execute('''select * from user where BNUM = %s''', [userID])
        return curs.fetchone()
    except:
        return None
        
        
# Gets all incidents reported about a specific facstaff user by their BNUM, and also the name of the students who reported
def getAllReportedFacstaff(conn, BNUM):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from incident inner join user where reporterID=BNUM and reportedID=%s''', [BNUM])
    return curs.fetchall()
    
# Gets all incidents reported by a specific student by their BNUM, and also the names of facstaff
def getAllReportedStudent(conn, BNUM):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from incident inner join user where reportedID=BNUM and reporterID=%s''', [BNUM])
    return curs.fetchall()
    
# # Gets all reported incidents (for admin view)
# def getAllIncidents(conn):
#     curs = conn.cursor(MySQLdb.cursors.DictCursor)
#     curs.execute('''select * from incident ''')
#     return curs.fetchall()
    
# Gets all reported incidents (for admin view)
# For some reason I'm getting reported.name... etc but not reporter.name, the reporter just shows up as "name"
def getAllIncidents(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from incident inner join user as reporter inner join 
                    user as reported where reporterID=reporter.BNUM and reportedID=reported.BNUM''')
    return curs.fetchall()

if __name__ == '__main__':
    conn = getConn('c9')
    # print(getAllReportedFacstaff(conn, 10000000))
    # print(getAllReportedStudent(conn, 1))
    print(getAllIncidents(conn))
