from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import smtplib
import random

app = Flask(__name__)
app.secret_key = b"_5#y2L'F4Q8z\n\xec]/"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
	_id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(255), unique=True)
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(255))
	first = db.Column(db.String(255))
	last = db.Column(db.String(255))
	posts = db.Column(db.Integer, default=0)
	liked_items = db.Column(db.Text, default="")
	saved_items = db.Column(db.Text, default="")
	commented_items = db.Column(db.Text, default="")
	comments = db.Column(db.Integer, default=0)
	friends = db.Column(db.Text, default="")
	groups = db.Column(db.Text, default="")
	friend_notifications = db.Column(db.Text, default="")
	share_notifications = db.Column(db.Text, default="")
	now_friend_notifications = db.Column(db.Text, default="")
	follower_notifications = db.Column(db.Text, default="")
	post_added_notifications = db.Column(db.Text, default="")
	half_friends = db.Column(db.Text, default="")
	received_posts = db.Column(db.Text, default="")
	followers = db.Column(db.Text, default="")
	following = db.Column(db.Text, default="")

	def __repr__(self):
		return f"{self.username} ({self.first} {self.last})"

class Post(db.Model):
	_id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(255))
	user_id = db.Column(db.Integer)
	title = db.Column(db.Text, nullable=False)
	body = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.String(10), nullable=False)
	likes = db.Column(db.Integer, default=0)
	saved = db.Column(db.Integer, default=0)
	comments = db.Column(db.Integer, default=0)
	group = db.Column(db.Integer, default=0)

class Comment(db.Model):
	_id = db.Column(db.Integer, primary_key=True, unique=True)
	username = db.Column(db.String(255))
	text = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.String(10), nullable=False)
	post_id = db.Column(db.Integer)

class Group(db.Model):
	_id = db.Column(db.Integer, primary_key=True, unique=True)
	name = db.Column(db.String(255), unique=True, nullable=False)
	admin = db.Column(db.Integer, nullable=False)
	description = db.Column(db.Text, default="")
	members = db.Column(db.Text, default=0, nullable=False)
	status = db.Column(db.String(10), default="public")
	posts = db.Column(db.Text, default="")

code = random.randrange(1000, 5000)
login_message = "You need to login or sign up first!"

def all_users():
	return User.query.all()

def all_posts():
	return Post.query.all()

def all_groups():
	return Group.query.all()

def get_user(column, value):
	try:
		if column == "_id": return User.query.filter_by(_id=value).first()
		if column == "username": return User.query.filter_by(username=value).first()
		if column == "email": return User.query.filter_by(email=value).first()
		if column =="first": return User.query.filter_by(first=value).first()
		if column == "last": return User.query.filter_by(last=value).first()
	except: return False

def get_id(username):
	try: return User.query.filter_by(username=username).first()._id
	except: return False

def get_email(_id):
	try: return User.query.filter_by(_id=_id).first().email
	except: return False

def get_password(_id):
	try: return User.query.filter_by(_id=_id).first().password
	except: return False

def get_first(_id):
	try: return User.quert.filter_by(_id=_id).first().first
	except: return False

def get_last(_id):
	try: return User.quert.filter_by(_id=_id).first().last
	except: return False

def get_post(column, value):
	try:
		if column == "_id": return Post.query.filter_by(_id=value).first()
		if column == "username": return Post.query.filter_by(username=value).all()
		if column == "user_id": return Post.query.filter_by(user_id=value).all()
		if column == "title": return Post.query.fitler_by(title=value).all()
		if column == "body": return Post.query.fitler_by(body=value).first()
		if column == "pub_date": return Post.query.filter_by(pub_date=value).first()
		if column == "group": return Post.query.filter_by(group=value).all()
	except: return False

def get_group(column, value):
	try:
		if column == "_id": return Group.query.filter_by(_id=value).first()
		if column == "name": return Group.query.filter_by(name=value).first()
		if column == "admin": return Group.query.filter_by(admin=value).first()
		if column == "description": return Group.query.fitler_by(description=value).first()
		if column == "members": return Group.query.fitler_by(members=value).first()
		if column == "status": return Group.query.filter_by(status=value).first()
	except: return False

def get_comment(column, value):
	try:
		if column == "_id": return Comment.query.filter_by(_id=value).first()
		if column == "username": return Comment.query.filter_by(username=value).all()
		if column == "text": return Comment.query.filter_by(text=value).all()
		if column == "pub_date": return Comment.query.filter_by(pub_date=value).all()
		if column == "post_id": return Comment.query.filter_by(post_id=value).all()
	except: return False

def all_comments():
	return Comment.query.all()

@app.route("/")
def index():
	if "username" in session:
		users = all_users()
		groups = all_groups()
		psts = reversed(all_posts())
		posts = []
		grps = []
		for post in psts:
			num = 97
			if len(post.body) > 100:
				if post.body[:num] == ".": post.body += ".."
				else: post.body = post.body[:num] + "..."
			if post.group:
				if get_group("_id", post.group).status == "public":
					posts.append(post)
					grps.append(get_group("_id", post.group))
			else:
				posts.append(post)
				grps.append(None)
		if len(posts) == 0: posts = False
		return render_template("index.html", posts=posts, user=get_user("username", session["username"]), groups=groups, grps=grps)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/notifications")
def notifications():
	notifications = False
	friend_notifications = []
	user = get_user("username", session["username"])
	for _id in user.friend_notifications.split():
		friend_notifications.append(get_user("_id", int(_id)))
		notifications = True
	share_notifications = {}
	for info in user.share_notifications.split():
		_id = int(info.split(":")[0])
		user_id = int(info.split(":")[1])
		share_notifications[get_post("_id", _id)] = get_user("_id", user_id)
		notifications = True
	now_friend_notifications = []
	for _id in user.now_friend_notifications.split():
		now_friend_notifications.append(get_user("_id", int(_id)))
		notifications = True
	follower_notifications = []
	for _id in user.follower_notifications.split():
		follower_notifications.append(get_user("_id", int(_id)))
		notifications = True
	added_post_notifications = []
	for _id in user.post_added_notifications.split():
		added_post_notifications.append(get_post("_id", int(_id)))
		notifications = True
	return render_template("notifications.html", notifications=notifications, friend_notifications=friend_notifications,\
		share_notifications=share_notifications, now_friend_notifications=now_friend_notifications, follower_notifications=follower_notifications,\
		added_post_notifications=added_post_notifications)

@app.route("/delete-notification-friend-<_id>")
def delete_notification_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		user.friend_notifications = user.friend_notifications.replace(_id + " ", "")
		db.session.commit()
		return redirect("/add-friend-" + _id)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-now-friend-<_id>")
def delete_notification_now_friend(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		user.now_friend_notifications = user.now_friend_notifications.replace(_id + " ", "")
		db.session.commit()
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-post-<info>")
def delete_notification_post(info):
	if "username" in session:
		user = get_user("username", session["username"])
		user.received_posts += info + " "
		user.share_notifications = user.share_notifications.replace(info + " ", "")
		db.session.commit()
		return redirect(info.split(":")[1] + "-post")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-now-following-<_id>")
def delete_notification_now_following(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		user.follower_notifications = user.follower_notifications.replace(_id + " ", "")
		db.session.commit()
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-notification-added-post-<_id>")
def delete_notification_added_post(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		user.post_added_notifications = user.post_added_notifications.replace(_id + " ", "")
		db.session.commit()
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/users")
def users():
	if "username" in session:
		users = all_users()
		return render_template("users.html", users=users, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/signup")
def signup():
	if "username" in session: return redirect(url_for("index"))
	return render_template("signup.html", user="")

@app.route("/login")
def login():
	if "username" in session: return redirect(url_for("index"))
	return render_template("login.html", user="")

@app.route("/loggingin", methods=["POST", "GET"])
def loggingin():
	if "username" in session: return redirect(url_for("index"))
	username = request.form.get("username")
	password = request.form.get("password")
	found_user = get_user("username", username)
	found_password = get_password(found_user._id) == password
	if found_user and found_password:
		_id = get_id(username)
		session["username"] = username
		session["email"] = get_email(found_user._id)
		session["password"] = get_password(_id)
		session["first"] = get_first(_id)
		session["last"] = get_last(_id)
		return redirect(url_for("index"))
	else:
		flash("Incorrect username or password. Sign up if you haven't got an account.")
		return redirect(url_for("login"))

@app.route("/signingup", methods=["POST", "GET"])
def signingup():
	if "username" in session: return redirect(url_for("index"))
	username = request.form.get("username")
	email = request.form.get("email")
	password = request.form.get("password")
	apassword = request.form.get("apassword")
	first = request.form.get("first")
	last = request.form.get("last")
	found_user = get_user("username", username)
	found_email = get_user("email", email)
	if found_user:
		flash("This username is already taken. Try another one.")
		return redirect(url_for("signup"))
	elif found_email:
		flash("This email is already in use. Try another one.")
		return redirect(url_for("signup"))
	else:
		if username != "" and password != "" and email != "" and first != "" and last != "":
			if password != apassword:
				flash("Passwords don't match. Please, try again.")
				return redirect(url_for("signup"))
			session["username"] = username
			session["email"] = email
			session["password"] = password
			session["first"] = first
			session["last"] = last
			return redirect(url_for("verify"))
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("signup"))

body = f"""{code} We need to verify your email. Please, copy and paste this code in your browser."""
message = f"""\
Subject: Email verification (Social Media App)

{body}
"""

@app.route("/verify")
def verify():
	flash(code)
	try:
		server = smtplib.SMTP("smtp.outlook.com", 587)
		server.starttls()
		server.login("bekhruzsniyazov@outlook.com", "microsoftpassword1")
		server.sendmail("bekhruzsniyazov@outlook.com", session["email"], message)
	except: pass
	return render_template("verify.html", user="")

@app.route("/verifying", methods=["POST", "GET"])
def verifying():
	flash(code)
	try:
		if int(request.form["code"]) == int(code):
			username = session["username"]
			email = session["email"]
			password = session["password"]
			first = session["first"]
			last = session["last"]
			user = User(username=username, email=email, password=password, first=first, last=last)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for("index"))
		else:
			flash("We were not able to verify your email. Please, sign up again.")
			session.pop("username", None)
			session.pop("email", None)
			session.pop("password", None)
			session.pop("first", None)
			session.pop("last", None)
			return redirect(url_for("signup"))
	except:
		flash("We were not able to verify your email. Please, sign up again.")
		session.pop("username", None)
		session.pop("email", None)
		session.pop("password", None)
		session.pop("first", None)
		session.pop("last", None)
		return redirect(url_for("signup"))

@app.route("/add")
def add():
	if "username" in session: return render_template("add.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/adding", methods=["POST", "GET"])
def adding():
	if "username" in session:
		post = request.form["post"]
		title = request.form["title"]
		if post != "" and title != "":
			date = str(datetime.now())[:10]
			date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
			user = get_user("username", session["username"])
			user.posts += 1
			for _id in user.followers.split():
				follower = get_user("_id", int(_id))
				follower.post_added_notifications += str(len(all_posts())+1) + " "
			pst = Post(username=session["username"], body=post, title=title, pub_date=date, user_id=user._id)
			db.session.add(pst)
			db.session.commit()
			return redirect(f"/{pst._id}-post")
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("add"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/settings")
def settings():
	if "username" in session:
		posts = len(get_post("username", session["username"]))
		user = get_user("username", session["username"])
		if posts > 0: delete = True
		else: delete = False
		return render_template("settings.html", user=user, delete=delete)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/logout")
def logout():
	session.pop("username", None)
	session.pop("email", None)
	session.pop("password", None)
	session.pop("first", None)
	session.pop("last", None)
	return redirect(url_for("login"))

@app.route("/change")
def change():
	if "username" in session:
		username = session["username"]
		email = session["email"]
		first = session["first"]
		last = session["last"]
		return render_template("change.html", username=username, email=email, first=first, last=last, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing", methods=["POST", "GET"])
def changing():
	if "username" in session:
		username = request.form["username"]
		first = request.form["first"]
		last = request.form["last"]
		user = get_user("username", session["username"])
		user.username = username
		user.first = first
		user.last = last
		db.session.commit()
		session["username"] = username
		session["first"] = first
		session["last"] = last
		return redirect(url_for("settings"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-account")
def delete_account():
	if "username" in session: return render_template("delete_account.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/deleting-account", methods=["POST", "GET"])
def deleting_account():
	if "username" in session:
		password = request.form["password"]
		usr = get_user("username", session["username"])
		if password == usr.password:
			if usr.posts > 0:
				users = all_users()
				posts = get_post("username", session["username"])
				ids = []
				for post in posts: ids.append(str(post._id))
				for user in users:
					for _id in ids:
						if _id in user.liked_items.split(): user.liked_items = user.liked_items.replace(f"{_id} ", "")
						if _id in user.saved_items.split(): user.saved_items = user.saved_items.replace(f"{_id} ", "")
						if _id in user.commented_items.split():
							user.commented_items = user.commented_items.replace(f"{_id} ", "")
							user.comments -= 1
						db.session.commit()
				for post in posts:
					if post.group:
						group = get_group("_id", post.group)
						group.posts = group.posts.replace(str(post._id) + " ", "")
						db.session.commit()
				for post in posts: db.session.delete(post)
			if usr.liked_items != "":
				for _id in usr.liked_items.split():
					if _id != "":
						_id = int(_id)
						post = get_post("_id", _id)
						post.likes -= 1
			if usr.saved_items != "":
				for _id in usr.saved_items.split():
					if _id != "":
						_id = int(_id)
						post = get_post("_id", _id)
						post.saved -= 1
			if usr.commented_items != "":
				for _id in usr.commented_items.split():
					if _id != "":
						_id = int(_id)
						post = get_post("_id", _id)
						post.comments -= 1
				for comment in get_comment("username", session["username"]): db.session.delete(comment)
			session.pop("username", None)
			session.pop("email", None)
			session.pop("password", None)
			session.pop("first", None)
			session.pop("last", None)
			if len(usr.friends.split()) > 0:
				for _id in usr.friends.split():
					if _id != "":
						_id = int(_id)
						friend = get_user("_id", _id)
						friend.friends = friend.friends.replace(f"{str(usr._id)} ", "")
						db.session.commit()

			for _id in usr.groups.split():
				group = get_group("_id", int(_id))
				for i in group.members.split():
					user = get_user("_id", int(i))
					user.group = user.groups.replace(_id + " ", "")
					db.session.commit()
				for i in group.posts.split():
					post = get_post("_id", int(i))
					user = get_user("_id", post.user_id)
					user.posts -= 1
					users = all_users()
					for user in users:
						if _id in user.liked_items.split(): user.liked_items = user.liked_items.replace(f"{_id} ", "")
						if _id in user.saved_items.split(): user.saved_items = user.saved_items.replace(f"{_id} ", "")
						if _id in user.commented_items.split():
							user.commented_items = user.commented_items.replace(f"{_id} ", "")
							user.comments -= 1
					db.session.delete(post)
					db.session.commit()

			db.session.delete(usr)
			db.session.commit()
		else:
			flash("Incorrect password. Try again.")
			return redirect(url_for("delete_account"))
		flash("Your account was successfully deleted.")
		return redirect(url_for("signup"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-all-password")
def delete_all_password():
	if "username" in session: return render_template("delete_all_password.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-all", methods=["POST", "GET"])
def delete_all():
	if "username" in session:
		usr = get_user("username", session["username"])
		if usr.password == request.form["password"]:
			usr.posts = 0
			posts = get_post("username", session["username"])
			ids = []
			for post in posts: ids.append(str(post._id))
			users = all_users()
			for user in users:
				for _id in ids:
					if _id in user.liked_items.split(): user.liked_items = user.liked_items.replace(f"{_id} ", "")
					if _id in user.saved_items.split(): user.saved_items = user.saved_items.replace(f"{_id} ", "")
					if _id in user.commented_items.split():
						user.commented_items = user.commented_items.replace(f"{_id} ", "")
						user.comments -= 1
					db.session.commit()
			for post in posts:
				if post.group:
					group = get_group("_id", post.group)
					group.posts = group.posts.replace(post._id, " ")
					db.session.commit()
			for post in posts: db.session.delete(post)
			db.session.commit()
			return redirect(url_for("settings"))
		else: return redirect(url_for("delete_all_password"))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-<_id>")
def delete(_id):
	if "username" in session:
		post = get_post("_id", int(_id))
		user = get_user("username", session["username"])
		user.posts -= 1
		users = all_users()
		for user in users:
			if _id in user.liked_items.split(): user.liked_items = user.liked_items.replace(f"{_id} ", "")
			if _id in user.saved_items.split(): user.saved_items = user.saved_items.replace(f"{_id} ", "")
			if _id in user.commented_items.split():
				user.commented_items = user.commented_items.replace(f"{_id} ", "")
				user.comments -= 1
		if post.group != 0:
			group = get_group("_id", int(post.group))
			group.posts = group.posts.replace(_id + " ", "")
		db.session.delete(post)
		db.session.commit()
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-comment-<_id>")
def delete_comment(_id):
	if "username" in session:
		_id = int(_id)
		comment = get_comment("_id", _id)
		user = get_user("username", session["username"])
		user.comments -= 1
		post = get_post("_id", comment.post_id)
		post.comments -= 1
		db.session.delete(comment)
		db.session.commit()
		return redirect(f"/{comment.post_id}-post")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/search")
def search():
	if "username" in session:
		return render_template("search.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/searching")
def searching():
	if "username" in session:
		query = request.args["q"].lower()
		posts = []
		users = []
		groups = []
		psts = all_posts()
		for post in psts:
			if post.title.lower().startswith(query): posts.append(post)
			for q in query.split():
				if post in posts: break
				for word in post.title.lower().split():
					if q == word or word.startswith(q) or q.startswith(word):
						posts.append(post)
						break
		usrs = all_users()
		for user in usrs:
			if user.username.lower().startswith(query): users.append(user)
			if user.first.lower().startswith(query) and user not in users: users.append(user)
			if user.last.lower().startswith(query) and user not in users: users.append(user)
		grps = all_groups()
		for group in grps:
			if group.name.lower().startswith(query): groups.append(group)
			for q in query.split():
				if group in groups: break
				for word in group.description.lower().split():
					if q == word:
						groups.append(group)
						break
		return render_template("result.html", posts=posts, users=users, groups=groups, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/change-password")
def change_password():
	if "username" in session: return render_template("password.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing-password", methods=["POST", "GET"])
def changing_password():
	if "username" in session:
		old_password = request.form["old_password"]
		new_password = request.form["new_password"]
		user = get_user("username", session["username"])
		if user.password == old_password:
			user.password = new_password
			db.session.commit()
			flash("Successefully changed password.")
			return redirect(url_for("settings"))
		else:
			flash("Incorrect old password. Try again.")
			return redirect(url_for("change_password"))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/library")
def library():
	if "username" in session:
		posts = get_post("username", session["username"])
		user = get_user("username", session["username"])
		friends = []
		for _id in user.friends.split():
			if _id != "":
				_id = int(_id)
				friend = get_user("_id", _id)
				if str(user._id) in friend.friends.split(): friends.append(friend)
		liked_posts = []
		for _id in user.liked_items.split():
			if _id != "": liked_posts.append(get_post("_id", int(_id)))
		saved_posts = []
		for _id in user.saved_items.split():
			if _id != "": saved_posts.append(get_post("_id", int(_id)))
		received_posts = {}
		for info in user.received_posts.split():
			user_id = int(info.split(":")[0])
			post_id = int(info.split(":")[1])
			usr = get_user("_id", user_id)
			post = get_post("_id", post_id)
			received_posts[post] = usr
		users = []
		for post in received_posts:
			usr = get_user("_id", post.user_id)
			users.append(usr)
		l_r_p = list(received_posts)
		groups = []
		for _id in user.groups.split(): groups.append(get_group("_id", int(_id)))
		followers = []
		for _id in user.followers.split(): followers.append(get_user("_id", int(_id)))
		following = []
		for _id in user.following.split(): following.append(get_user("_id", int(_id)))
		return render_template("library.html", posts=posts, liked_posts=liked_posts, saved_posts=saved_posts, friends=friends, groups=groups, user=user, received_posts=received_posts, users=users, l_r_p=l_r_p, followers=followers, following=following)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/share-<_id>")
def share(_id):
	if "username" in session:
		_id = int(_id)
		post = get_post("_id", _id)
		friends = []
		user = get_user("username", session["username"])
		for _id in user.friends.split():
			if _id != "":
				_id = int(_id)
				friend = get_user("_id", _id)
				friends.append(friend)
		return render_template("share.html", post=post, friends=friends, user=user)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/sharing-<info>")
def sharing(info):
	if "username" in session:
		user_id = int(info.split(":")[0])
		_id = int(info.split(":")[1])
		post_id = int(info.split(":")[2])
		user = get_user("_id", user_id)
		user.share_notifications += str(_id) + ":" + str(post_id) + " "
		db.session.commit()
		return redirect(f"share-{_id}")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-comment-<_id>", methods=["POST", "GET"])
def add_comment(_id):
	if "username" in session:
		_id = int(_id)
		text = request.form["text"]
		date = str(datetime.now())[:10]
		date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
		comment = Comment(_id = len(all_comments())+1, username=session["username"], text=text, pub_date=date, post_id=_id)
		db.session.add(comment)
		user = get_user("username", session["username"])
		user.comments += 1
		user.commented_items += f"{_id} "
		post = get_post("_id", _id)
		post.comments += 1
		db.session.commit()
		return redirect(f"{_id}-post")
	flash(login_message)
	return redirect(url_for("login"))


@app.route("/<_id>-post")
def post(_id):
	if "username" in session:
		_id = int(_id)
		post = get_post("_id", _id)
		user = get_user("username", session["username"])
		group = None
		if post.group:
			group = get_group("_id", post.group)
			if group.status == "private":
				if str(user._id) not in group.members.split(): return redirect(url_for("index"))
		liked_items = user.liked_items.split()
		saved_items = user.saved_items.split()
		likeable = True
		saveable = True
		if str(_id) in liked_items: likeable = False
		if str(_id) in saved_items: saveable = False
		comments = get_comment("post_id", _id)
		comments.reverse()
		delete = []
		for comment in comments:
			if comment.username == session["username"]: delete.append(comment)
		return render_template("post.html", post=post, likeable=likeable, saveable=saveable, comments=comments, delete=delete, user=user, _id=post.user_id, group=group)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-save")
def save(_id):
	if "username" in session:
		post = get_post("_id", int(_id))
		user = get_user("username", session["username"])
		if str(post._id) not in user.saved_items.split():
			user.saved_items += str(post._id) + " "
			post.saved += 1
			db.session.commit()
		return jsonify(post.saved)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-like")
def like(_id):
	if "username" in session:
		post = get_post("_id", int(_id))
		user = get_user("username", session["username"])
		if str(post._id) not in user.liked_items.split():
			user.liked_items += str(post._id) + " "
			post.likes += 1
			db.session.commit()
		return jsonify(post.likes)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-friend-<_id>")
def add_friend(_id):
	if "username" in session:
		_id = int(_id)
		user = get_user("username", session["username"])
		if str(_id) not in user.friends.split():
			friend = get_user("_id", _id)
			if str(user._id) not in friend.half_friends.split():
				if str(_id) not in user.half_friends.split():
					user.half_friends += str(_id) + " "
					friend.friend_notifications += str(user._id) + " "
					db.session.commit()
					flash(f"Waiting for @{friend.username} to accept your friendship.")
				return redirect(f"/{friend._id}")
			else:
				friend.half_friends = friend.half_friends.replace(str(user._id) + " ", "")
				user.friends += str(_id) + " "
				friend.friends += str(user._id) + " "
				friend.now_friend_notifications += str(user._id) + " "
				db.session.commit()
				flash(f"@{friend.username} is now your friend.")
				return redirect(url_for("index"))
		else: return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-friend-<_id>")
def delete_friend(_id):
	if "username" in session:
		_id = int(_id)
		user = get_user("username", session["username"])
		friend = get_user("_id", _id)
		user.friends = user.friends.replace(f"{str(_id)} ", "")
		friend.friends = friend.friends.replace(f"{str(user._id)} ", "")
		db.session.commit()
		return redirect(url_for("library"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/create-group")
def create_group():
	if "username" in session:
		return render_template("create_group.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/creating-group", methods=["POST", "GET"])
def creating_group():
	if "username" in session:
		name = request.form["name"]
		description = request.form["description"]
		try: status = request.form["status"]
		except:
			flash("You need to select the status of the group!")
			return redirect(url_for("create_group"))
		if name != "" and description != "" and status != "":
			user = get_user("username", session["username"])
			group = Group(name=name, admin=user._id, description=description, members=str(user._id)+" ", status=status)
			db.session.add(group)
			group = get_group("_id", len(all_groups()))
			user.groups += f"{group._id} "
			db.session.commit()
			return redirect(f"{group._id}-group")
		else:
			flash("You need to fill all the fields!")
			return redirect(url_for("create_group"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>-group")
def group(_id):
	if "username" in session:
		_id = int(_id)
		group = get_group("_id", _id)
		if not group: return redirect(url_for("index"))
		user = get_user("username", session["username"])
		member = False
		if str(group._id) in user.groups.split(): member = True
		if not member and group.status == "private":
			flash("You cannot see the posts inside of this group because this group is private.")
			return redirect(url_for("index"))
		members = []
		admin = False
		if group.admin == user._id: admin = True
		for i in group.members.split():
			if i != "":
				mmbr = get_user("_id", int(i))
				members.append(mmbr)
		administrator = get_user("_id", group.admin).username
		psts = get_post("group", _id)
		posts = []
		delete = []
		if psts:
			for post in psts:
				if post.username == session["username"]: delete.append(post)
				num = 97
				if len(post.body) > 100:
					if post.body[:num] == ".": post.body += ".."
					else: post.body = post.body[:num] + "..."
				posts.append(post)
		return render_template("group.html", group=group, members=members, len=len(members), member=member, admin=admin, user=user, administrator=administrator, posts=posts, delete=delete)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/invite-<_id>")
def invite(_id):
	if "username" in session:
		_id = int(_id)
		group = get_group("_id", _id)
		user = get_user("username", session["username"])
		friends = []
		for _id in user.friends.split():
			if _id != "":
				_id = int(_id)
				friend = get_user("_id", _id)
				if str(group._id) not in friend.groups.split(): friends.append(friend)
		return render_template("invite.html", group=group, friends=friends, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/inviting-<info>")
def inviting(info):
	if "username" in session:
		friend_id = int(info.split(":")[0])
		_id = int(info.split(":")[1])
		group = get_group("_id", _id)
		group.members += f"{friend_id} "
		user = get_user("_id", friend_id)
		user.groups += f"{group._id} "
		db.session.commit()
		return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/invite-users-<_id>")
def invite_users(_id):
	if "username" in session:
		_id = int(_id)
		group = get_group("_id", _id)
		user = get_user("username", session["username"])
		if user._id == group.admin:
			users = []
			for user in all_users():
				if str(group._id) not in user.groups.split(): users.append(user)
			return render_template("invite_users.html", group=group, users=users, user=user)
		else:
			flash("You cannot invite users to this group unless they are your friends.")
			return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/remove-from-group-<info>")
def remove_from_group(info):
	if "username" in session:
		user_id = int(info.split(":")[0])
		_id = int(info.split(":")[1])
		user = get_user("_id", user_id)
		group = get_group("_id", _id)
		user.groups = user.groups.replace(f"{str(_id)} ", "")
		group.members = group.members.replace(f"{user_id} ", "")
		db.session.commit()
		return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/change-admin-<_id>")
def change_admin(_id):
	if "username" in session:
		group = get_group("_id", int(_id))
		members = []
		for _id in group.members.split():
			member = get_user("_id", int(_id))
			members.append(member)
		return render_template("change_admin.html", group=group, members=members)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/changing-admin-<info>")
def changing_admin(info):
	if "username" in session:
		user_id = int(info.split(":")[0])
		group_id = int(info.split(":")[1])
		group = get_group("_id", group_id)
		group.admin = user_id
		db.session.commit()
		return redirect(f"/{group_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-<_id>")
def add_post_group(_id):
	if "username" in session: return render_template("add_inside_group.html", _id=_id, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/adding-inside-<_id>", methods=["POST", "GET"])
def adding_post_group(_id):
	if "username" in session:
		title = request.form["title"]
		body = request.form["post"]
		if title != "" and body != "":
			date = str(datetime.now())[:10]
			date = f"{date[5]}{date[6]}/{date[-2]}{date[-1]}/{date[0]}{date[1]}{date[2]}{date[3]}"
			user = get_user("username", session["username"])
			post = Post(username=session["username"], body=body, title=title, pub_date=date, user_id=user._id, group=int(_id))
			db.session.add(post)
			db.session.commit()
			group = get_group("_id", int(_id))
			post = get_post("_id", len(all_posts()))._id
			group.posts += str(post) + " "
			user = get_user("username", session["username"])
			user.posts += 1
			db.session.commit()
			return redirect(f"/{_id}-group")
		else:
			flash("You need to fill all the fields!")
			return redirect(f"/add-{_id}")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/add-follower-<info>")
def add_follower(info):
	if "username" in session:
		user = get_user("_id", int(info.split(":")[0]))
		follower = get_user("_id", int(info.split(":")[1]))
		if str(follower._id) not in user.following.split():
			user.following += str(follower._id) + " "
			follower.followers += str(user._id) + " "
		follower.follower_notifications += str(user._id) + " "
		db.session.commit()
		return redirect("/" + str(follower._id))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/unfollow-<_id>")
def unfollow(_id):
	if "username" in session:
		user = get_user("username", session["username"])
		user.following = user.following.replace(_id + " ", "")
		following = get_user("_id", int(_id))
		following.followers = following.followers.replace(str(user._id) + " ", "")
		db.session.commit()
		return redirect(url_for("index"))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-group-password-<_id>")
def delete_group_password(_id):
	if "username" in session: return render_template("delete_group.html", _id=_id, user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/delete-group-<_id>", methods=["POST", "GET"])
def delete_group(_id):
	if "username" in session:
		password = request.form["password"]
		_id = int(_id)
		user = get_user("username", session["username"])
		if user.password == password:
			group = get_group("_id", _id)
			for i in group.members.split():
				usr = get_user("_id", int(i))
				usr.groups = usr.groups.replace(str(_id) + " ", "")
				db.session.commit()
			for i in group.posts.split():
				post = get_post("_id", int(i))
				usr = get_user("_id", post.user_id)
				usr.posts -= 1
				users = all_users()
				for user in users:
					if _id in user.liked_items.split(): user.liked_items = user.liked_items.replace(f"{_id} ", "")
					if _id in user.saved_items.split(): user.saved_items = user.saved_items.replace(f"{_id} ", "")
					if _id in user.commented_items.split():
						user.commented_items = user.commented_items.replace(f"{_id} ", "")
						user.comments -= 1
				db.session.delete(post)
				db.session.commit()
			db.session.delete(group)
			db.session.commit()
			return redirect(url_for("index"))
			db.session.commit()
		else:
			flash("Incorrect password.")
			return redirect(f"/{_id}-group")
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/searching-<info>")
def searching_friends(info):
	if "username" in session:
		usrs = info.split(":")[0]
		_id = int(info.split(":")[1])
		user = get_user("username", session["username"])
		group = get_group("_id", int(_id))
		query = request.args["q"].lower()
		l = []
		if usrs == "friends":
			for _id in user.friends.split():
				friend = get_user("_id", int(_id))
				l.append(friend)
		else:
			tmp = all_users()
			tmp.remove(user)
			l = tmp
		users = []
		for u in l:
			if u.username.lower().startswith(query): users.append(u)
			if u.first.lower().startswith(query) and u not in users: users.append(u)
			if u.last.lower().startswith(query) and u not in users: users.append(u)
		return render_template("result_invite.html", users=users, group=group)
	flash(login_message)
	return redirect(url_for("login"))

@app.route("/<_id>")
def user(_id):
	if "username" in session:
		try: _id = int(_id)
		except: return render_template("error.html")
		user = get_user("_id", _id)
		if user:
			posts = get_post("username", user.username)
			friend = True
			follower = False
			followers = []
			following = []
			current_user = get_user("username", session["username"])
			if user._id != current_user._id and str(user._id) not in current_user.friends.split(): friend = False
			if str(current_user._id) in user.followers.split(): follower = True
			friends = []
			if friend or session["username"] == user.username:
				for _id in user.friends.split(): friends.append(get_user("_id", int(_id)))
			groups = []
			for _id in user.groups.split(): groups.append(get_group("_id", int(_id)))
			for _id in user.followers.split(): followers.append(get_user("_id", int(_id)))
			for _id in user.following.split(): following.append(get_user("_id", int(_id)))
			return render_template("user.html",\
				username=user.username, email=user.email, first=user.first, last=user.last, number=user.posts, posts=posts, friend=friend, friends=friends, user=current_user, groups=groups, _id=user._id, follower=follower, followers=followers, followers_num=len(followers), following=following, following_num=len(following))
		return render_template("error.html", user=get_user("username", session["username"]))
	flash(login_message)
	return redirect(url_for("login"))

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)