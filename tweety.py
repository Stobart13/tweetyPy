from bottle import route, request, debug, run, template
import urllib2
import twurl
import json
import sqlite3
import pickle
from operator import itemgetter

session = {'logins': 0, 'name': '','archiveID':1}
userResult = 0


def checkLogin(name, password):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * from users where name=? and password=?",(name,password))
    usernameExists = len(cursor.fetchall())
    if usernameExists:
        return True
    else:
        return False
    cursor.close()
    connect.close()



def makeMenu():
    global userResult
    global session
    menu = "<h4>Current User</h4>"
    menu += "<a class='menuItem' href='/'>" + session['name']+ "'s Timeline"+ "</a><br>"
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select id from users where name=?",(session['name'],))
    userResult = cursor.fetchone()
	
    cursor.execute("select id, name from archives order by name asc")
    result = cursor.fetchall()
	
  #  cursor.execute("select id, name from archives order by name asc")
    cursor.execute("select id from users where name=?",(session['name'],))
    thisResult = cursor.fetchone()
	
    cursor.execute("select archives.name, archives.id from archives, sharedArchive where archives.id=sharedArchive.sharedArchiveID and sharedArchive.sharedUserID=?", (thisResult))
    sharedArchive = cursor.fetchall()
    cursor.close()
    connect.close()
	
    menu+="<h3>My Archives</h3>"
    for archive in result:
        menu += "<a class='menuItem' href='/showArchive/" + str(archive[0]) + "'>" + (archive[1]) + "</a><br>"
		
    menu += "<h3>Shared Archives</h3>"
    for archive in sharedArchive:
        menu += "<a class='menuItem' href='/showSharedArchive/" + str(archive[1]) + "'>" + str(archive[0]) + "</a><br>"
    menu += '''<form method='post' action='/addArchive'>
	            <input type='text' name='newArchive' size='15'><br>
	            <input type='submit' name='submit' value='New Archive'>
	            </form>'''
    menu+= "<button><a class='btn btn-danger' href='/logout'>Logout</a></button>"
    return menu

def getArchiveName():
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select name from archives where id=?", (session['archiveID'],))
    result = cursor.fetchone()
    cursor.close()
    connect.close()
    return "Archive: " + str(result[0])

def callAPI(twitter_url, parameters):
    url = twurl.augment(twitter_url, parameters)
    connection = urllib2.urlopen(url)
    return connection.read()

def shareArchiveDropdown():
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select id, name from users order by name asc")
    result = cursor.fetchall()
    cursor.close()
    connect.close()
    html = "<form name='shareArchive' method='post' action='/shareArchive'>"
    html += "<select name='sharedUserID' onchange='form.submit()' >"
    html += "<option>Share with...</option>"
    for name in result:
        html += "<option value='" + str(name[0]) + "'>" + name[1] + "</option>"
    html+= "</select>"
    html+= "</form>"
    return html

@route('/shareArchive', method='post')
def shareArchive():
    global session
    global userResult
    id = request.POST.get('sharedUserID','').strip()
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("INSERT into sharedArchive(sharedArchiveID, ownerID, sharedUserID) VALUES(?,?,?) ",(str(session['archiveID']), str(session['name']),id,))
    connect.commit()
    cursor.close()
    connect.close()
    html = showMyTimeline()
    return template('showTweets.tpl', heading="My timeline",menu=makeMenu(),html=html)


def makeArchiveDropdown():
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select id, name from archives order by name asc")
    result = cursor.fetchall()
    cursor.close()
    connect.close()
    html = "<select name='archiveID' onchange='form.submit()'>"
    html += "<option>Save to...</option>"
    for archive in result:
        html += "<option value='" + str(archive[0]) + "'>" + archive[1] + "</option>"
    html += "</select>"
    return html


def makeTweet(item, mode, archiveList):	
	html, tweetHTML, links = '', '', ''	
	if mode=='myTimeline':
		links = "<form name='archive' method='post' action='/archive'>"
		links += "<input type='hidden' name='tweetID' value='" + str(item['id']) + "'>"
		links += archiveList
		links += "</form>"
	elif mode=='archive':
			links="<a href='/moveUp/" + str(item['id']) + "'>Up</a><br>" + \
		      "<a href='/moveDown/" + str(item['id']) + "'>Down</a><br>" +\
		      "<a href='/deleteTweet/" + str(item['id']) + "'>Delete</a>"
		
	html += "<table><tr valign='top'><td>"
	html += "<img src='" + item['user']['profile_image_url'] + "'></td>"
	html += "<td><a href='/user/" + item['user']['screen_name'] + "'>@" + item['user']['screen_name'] + "</a>"
	html += " (" + item['user']['name'] + ")"
	html += "</td></tr>"
	
	tweetlinks = []

	if 'user_mentions' in item['entities']:
		for user in item['entities']['user_mentions']:
			tweetlinks.append([user['indices'][0], user['indices'][1], 'user', user['screen_name']])
			
	if 'hashtags' in item['entities']:
		for hashtag in item['entities']['hashtags']:
			tweetlinks.append([hashtag['indices'][0], hashtag['indices'][1], 'hashtag', hashtag['text']])
			
	if 'urls' in item['entities']:
		for url in item['entities']['urls']:
			tweetlinks.append([url['indices'][0], url['indices'][1], 'url', url['url'], url['expanded_url']])
			
	if 'media' in item['entities']:
		for media in item['entities']['media']:
			tweetlinks.append([media['indices'][0], media['indices'][1], 'media', media['media_url'], media['display_url']])
			
	sortedLinks = sorted(tweetlinks, key=itemgetter(0))
	
	ptr = 0
	for tweetlink in sortedLinks:
		tweetHTML = tweetHTML + item['text'][ptr:int(tweetlink[0])]
		if tweetlink[2] == 'user':
			tweetHTML += "<a href='/user/" + tweetlink[3] + "'>@" + tweetlink[3] + "</a>"
			
		if tweetlink[2] == 'hashtag':
			tweetHTML += "<a href='/hashtags/" + tweetlink[3] + "'>#" + tweetlink[3] + "</a>"
			
		if tweetlink[2] == 'url':
			tweetHTML += "<a href='" + tweetlink[3] + "'>" + tweetlink[4] + "</a>"
			
		if tweetlink[2] == 'media':
			tweetHTML += "<br><img src='" + tweetlink[3] + "'></img>"
			
		ptr = tweetlink[1]
	tweetHTML = tweetHTML + item['text'][ptr:]
	
	html += "<tr><td>" + links + "</td><td>" + tweetHTML + "<br>"
	html += "</td></tr></table><hr>"
	return html

def showMyTimeline():
    twitter_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
    parameters = {'count': 5}
    data = callAPI(twitter_url, parameters)
    js = json.loads(data)
    html, archives = '', makeArchiveDropdown()
    for item in js:
        html = html + makeTweet(item, 'myTimeline', archives)
    return html

def getTweet(id):
    twitter_url = 'https://api.twitter.com/1.1/statuses/show.json'
    parameters = {'id': id}
    data = callAPI(twitter_url, parameters)
    return json.loads(data)


def showStoredTweets(archiveID):
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("select tweet from tweets where archiveID=? order by position asc", (archiveID,))
    result = cursor.fetchall()
    cursor.close()
    connect.close()
    html = ''
    html = html + shareArchiveDropdown()
    for tweet in result:
        html = html + makeTweet(pickle.loads(tweet[0]), 'archive', '')
    return html

def searchForTweets(searchTerm):
    twitter_url = 'https://api.twitter.com/1.1/search/tweets.json'
    url = twurl.augment(twitter_url, {'q': searchTerm, 'count': 5})
    connection = urllib2.urlopen(url)
    data = connection.read()
    js = json.loads(data)
    html = ''

    for item in js['statuses']:
        html = html + makeTweet(item, 'myTimeline', '')
    return html


@route('/archive', method='post')
def archiveTweet():
    global session
    archiveID = request.POST.get('archiveID', '').strip()
    tweetID = request.POST.get('tweetID', '').strip()
    pickledTweet = pickle.dumps(getTweet(tweetID))
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT position from tweets where archiveID=? ORDER BY position DESC LIMIT 1",
                   (session['archiveID'],))
    dbRow = cursor.fetchone()
    if dbRow is not None:
        nextPosition = int(dbRow[0]) + 1
    else:
        nextPosition = 1
    cursor.execute("INSERT INTO tweets (tweetID, tweet, archiveID, position) VALUES (?,?,?,?)", \
                   (tweetID, sqlite3.Binary(pickledTweet), archiveID, nextPosition))
    connect.commit()
    cursor.close()
    connect.close()
    session['archiveID'] = archiveID
    html = showStoredTweets(archiveID)
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html)

@route('/deleteTweet/<id>')
def deleteTweet(id):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("DELETE from tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
    connect.commit()
    cursor.close()
    connect.close()
    html = showStoredTweets(session['archiveID'])
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html,logins=session['logins'], name=session['name'])

@route('/moveUp/<id>')
def moveUp(id):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT position FROM tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
    position = cursor.fetchone()[0]
    cursor.execute("SELECT tweetID, position FROM tweets WHERE position<? and archiveID=? order by position desc limit 1", (position,session['archiveID']))
    dbRow = cursor.fetchone()
    if dbRow is not None:
        otherID, otherPosition = dbRow[0], dbRow[1]
        cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=? ", (otherPosition,id,session['archiveID']))
        cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=?", (position,otherID,session['archiveID']))
        connect.commit()
    cursor.close()
    connect.close()
    html = showStoredTweets(session['archiveID'])
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html)

@route('/moveDown/<id>')
def moveDown(id):
    global session
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT position FROM tweets WHERE tweetID=? and archiveID=?", (id,session['archiveID']))
    position = cursor.fetchone()[0]
    cursor.execute("SELECT tweetID, position FROM tweets WHERE position>? and archiveID=? order by position desc limit 1", (position,session['archiveID']))
    dbRow = cursor.fetchone()
    if dbRow is not None:
        otherID, otherPosition = dbRow[0], dbRow[1]
        cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=? ", (otherPosition,id,session['archiveID']))
        cursor.execute("UPDATE tweets set position=? WHERE tweetID=? and archiveID=?", (position,otherID,session['archiveID']))
        connect.commit()
    cursor.close()
    connect.close()
    html = showStoredTweets(session['archiveID'])
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html)

@route('/showArchive/<id>')
def showArchive(id):
    global session
    session['archiveID'] = id
    html = showStoredTweets(id)
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html)
	
@route('/showSharedArchive/<id>')
def showSharedArchive(id):
    global session
    session['archiveID'] = id
    html = showStoredTweets(id)
    return template('showTweets.tpl', heading=getArchiveName(), menu=makeMenu(), html=html)


@route('/addArchive', method='post')
def addArchive():
    global session
    newArchive = request.POST.get('newArchive','').strip()
    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    if newArchive != "":
        cursor.execute("INSERT into archives (name) VALUES (?)", (newArchive,))
        cursor.execute("select id from archives where name=?", (newArchive,))
        archiveID = cursor.fetchone()
        cursor.execute("INSERT into sharedArchive (sharedArchiveID, ownerID, sharedUserID) VALUES (?,?,?) ",(str([archiveID[0]]), str(session['name']), '',))
        connect.commit()
    cursor.close()
    connect.close()
    html = showMyTimeline()
    return template('showTweets.tpl', heading="My timeline", menu=makeMenu(), html=html)


@route('/')
def login_form():
    html = showMyTimeline()
    if session['name'] != '':
        return template('showTweets.tpl', message="You are already logged in!",
                        success=True, heading="My Timeline", html=html, menu=makeMenu(), logins=session['logins'],
                        name=session['name'])
    else:
        return template('login.tpl')

@route('/hashtags/<hashtag>')
def hashtags(hashtag):
    user = "#" + hashtag
    html = searchForTweets(hashtag)
    return template('showTweets.tpl',heading="#" + hashtag + " results: ",menu=makeMenu(), html=html)

@route('/userMentions/<user>')
def userMentions(user):
    user = "@" + user
    html = searchForTweets(user)
    return template('showTweets.tpl',heading="User Mentions: " + user,menu=makeMenu(), html=html)

@route('/user/<user>')
def showUserTimeline(user):
    twitter_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    parameters = {'screen_name': '@' + user, 'count': 5}
    data = callAPI(twitter_url, parameters)
    js = json.loads(data)
    html = ''
    for item in js:
        html = html + makeTweet(item,'myTimeline','')
    return template('showTweets.tpl',heading="User Mentions: " + user, menu=makeMenu(), html=html)


@route('/home', method='post')
def login_submit():
    global session
    name = request.forms.get('name')
    password = request.forms.get('password')
    html=showMyTimeline()
    if checkLogin(name, password):
        session['logins'] = session['logins'] + 1
        session['name'] = name
        return template('showTweets.tpl', heading="My timeline",menu=makeMenu(),html=html,message='Successfully logged in!', success=True, name=session['name'],
                        logins=session['logins'])
    else:
        return template('loggedIn2.tpl', message='Unlucky! Try again.', success=False, name=session['name'],
                        logins=session['logins'])


@route('/newUser')
def new_user():
    return template('new_user.tpl', message = 'Please provide username')


@route('/newUserStore', method='post')
def new_user_store():
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()

    connect = sqlite3.connect('twitterDB.db')
    cursor = connect.cursor()
    cursor.execute("SELECT count(*) from users where name=?", (username,))
    result = cursor.fetchone()
    if result[0] > 0:
        cursor.close()
        connect.close()
        return template('new_user.tpl', message='Username already present - try again')
    else:
        cursor.execute("INSERT INTO users (name, password) VALUES (?,?)", (username, password))
        new_id = cursor.lastrowid
        connect.commit()
        cursor.close()
        connect.close()
        return '<p>The new user was inserted into the database, the ID is %s <button><a href="/">Log In</a></button></p>' % new_id 
		
@route('/login')
def login_form():

    return template('login.tpl')

@route('/logout')
def logout():
    session['logins'] = 0
    session['name'] = ''
    return template('login.tpl')


debug(True)
run(reloader=True)
