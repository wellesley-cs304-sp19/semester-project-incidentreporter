

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
        
    if uid:
        conn = incidentReporter.getConn('c9')
        print (uid)
        userInfo = incidentReporter.getUserInformation(conn, uid)
        print(userInfo)
    return render_template('home.html',
                            userID = uid, 
                            userInfo = userInfo)

# @app.route('/rateMovie/', methods=['GET','POST'])
# def rate_movie(searchTerm=None, json=None):
#     conn = incidentReporter.getConn('wmdb')
    
#     if searchTerm == None:
#         movies = incidentReporter.getAllMovies(conn)
#     elif searchTerm:
#         movies = incidentReporter.getMovieByTitle(conn, searchTerm)
    
        
    
#     try:
#         uid = session['UID']
#     except:
#         uid = None
        
#     if request.method == 'GET':
#         return render_template('movie-list.html',
#                           movieList=movies,
#                           userID = uid)


# @app.route('/setUID/', methods=['POST'])
# def setUID():
#     if request.method == 'POST':
#         uid = request.form.get('user_id')
#         session['UID'] = uid
        
#         return redirect(request.referrer)
               
# @app.route('/updateRating/', methods=['POST'])
# def updateRating():
    
#     if request.method == 'POST':
#         try:
#             uid = session['UID']
            
#         except:
#             flash("you must be logged in to rate a movie")
#             return redirect(request.referrer)
            
#         try:
#             conn = incidentReporter.getConn('wmdb')
#             tt = request.form.get('tt')
#             rating = request.form.get('stars')
            
#             incidentReporter.updateUserRating(conn, uid, tt, rating)
#             newAvg = incidentReporter.calculateAverage(conn, tt)
            
#             flash ("New average rating of " + str(newAvg['avg_rating']))
#             return redirect(request.referrer)
            
#         except:
#             flash("please try again later")
#             return redirect(request.referrer)
        
        
          
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
