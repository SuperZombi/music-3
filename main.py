import os
import shutil
import time
from pathlib import Path
from dateutil import parser as dataparse
from flask import Flask, request, jsonify, send_from_directory, send_file, abort, redirect, Response
from flask_cors import CORS
import json
import filetype
from PIL import Image, ImageSequence
from io import BytesIO
import audio_metadata
import warnings
warnings.filterwarnings('ignore')
from fuzzywuzzy import fuzz
# import re
from tools.DataBase import DataBase
from tools.serverErrors import Errors
from tools.BrootForceProtection import BrootForceProtection
import tools.htmlTemplates as htmlTemplates
from textwrap import dedent
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route("/status")
def status():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	return jsonify({'online': True, 'time': int(time.time()),
					'ip': ip})

@app.route("/")
def index():
	return send_from_directory('data', 'index.html')

@app.errorhandler(404)
def page_not_found(e):
	return send_from_directory('data', '404.html'), 404
@app.errorhandler(403)
def page_not_found(e):
	return send_from_directory('data', '403.html'), 403

@app.route('/<path:filepath>')
def data(filepath):
	p = os.path.join("data", filepath)
	if os.path.exists(p):
		if os.path.isfile(p):
			if filetype.is_image(p):
				if 'size' in request.args.keys():
					if request.args['size'] == "small":
						try:
							img = Image.open(p)
							buf = BytesIO()
							if 'loop' in img.info:
								frames = ImageSequence.Iterator(img)
								def resize(frames, size):
									for frame in frames:
										thumbnail = frame.copy()
										thumbnail.thumbnail(size, Image.ANTIALIAS)
										yield thumbnail

								frames = list(resize(frames, (200, 200)))
								frames[0].save(buf, img.format, save_all=True, append_images=frames)
							else:
								img.thumbnail((200, 200), Image.ANTIALIAS)
								img.save(buf, img.format)

							buf.seek(0)
							return send_file(buf, mimetype=filetype.guess(p).mime)
						except:
							None
			stat_check_html(filepath, True)
			return send_from_directory('data', filepath)
		if filepath[-1] != "/":
			return redirect("/" + filepath + "/")
		if os.path.isfile(os.path.join(p, 'index.html')):
			stat_check_html(filepath)
			return send_from_directory('data', os.path.join(filepath, 'index.html'))
	if os.path.isfile(p + '.html'):
		stat_check_html(filepath)
		return send_from_directory('data', filepath + '.html')
	abort(404)

@app.route("/api/lang_detect")
def lang_detect():
	return send_from_directory('tools', 'lang_detect.html')

@app.route("/api/decode_error", methods=["POST"])
def get_error_value():
	if 'lang' in request.json.keys():
		lang = request.json['lang'].lower()

	try:
		temp = Errors[request.json['code']].value
		if isinstance(temp, dict):
			if lang in temp.keys():
				return {'successfully': True, 'value': temp[lang]}
			return {'successfully': True, 'value': temp['en']} # default
		return temp
	except:
		return {'successfully': False}


def stat_check_html(file, sub=False):
	def stat_check(path):
		path = os.path.dirname(path)
		def is_track_path(path):
			parts = Path(path).parts
			if len(parts) == 2 and parts[0] != "account":
				return True
			return False

		if is_track_path(path):
			track = tracks.find(path=list(Path(path).parts))
			tracks.get(track)['statistics']["views"] += 1
			tracks.save()
	if sub:
		if os.path.splitext(file)[-1] == ".html":
			if Path(file).parts[0] != "root_":
				try: stat_check(file)
				except: None
	else:
		try: stat_check(file)
		except: None




tracks = DataBase("database/tracks.bd")
users = DataBase("database/users.bd", unique="user")

# Method not implemented
# from math import sqrt
# def wilson_score(likes, views, votes_range = [0, 1]):
# 	if likes > views: return 1
# 	z = 1.64485
# 	v_min = min(votes_range)
# 	v_width = float(max(votes_range) - v_min)
# 	phat = (likes - views * v_min) / v_width / float(views)
# 	rating = (phat+z*z/(2*views)-z*sqrt((phat*(1-phat)+z*z/(4*views))/views))/(1+z*z/views)
# 	return rating * v_width + v_min

def my_rating(likes, views):
	if likes == 0 or views == 0: return 0
	return (likes / views * likes) * (views / likes * views)


def sort_tracks(tracks, by):
	if by == "date":
		tracks = sorted(tracks, key=lambda x: dataparse.parse(x["date"], dayfirst=True) , reverse=True)
	elif by == "popular":
		tracks = sorted(tracks, key=lambda x: my_rating(x["statistics"]["likes"], x["statistics"]["views"]) , reverse=True)
	return tracks

@app.route('/api/get_tracks', methods=["POST"])
def get_tracks():
	allowed_sort_methods = ["date", "popular"]
	sort_method = "date"
	if 'sort_method' in request.json.keys():
		if request.json['sort_method'] in allowed_sort_methods:
			sort_method = request.json['sort_method']

	if 'user' in request.json.keys():
		user = users.get(request.json['user'])
		if user:
			temp = {}
			temp['path'] = request.json['user'].lower().replace(" ", "-")
			temp['tracks'] = []

			ids = tracks.find_all(artist=request.json['user'])
			for id in ids:
				track = tracks.get(id)
				temp['tracks'].append(track)

			temp['tracks'] = sort_tracks(temp['tracks'], by=sort_method)

			return jsonify({'successfully': True, **temp})
		else:
			return jsonify({'successfully': False, 'reason': Errors.user_dont_exist.name})

	temp = sort_tracks(tracks.data, by=sort_method)
	return jsonify({'successfully': True, 'tracks': temp})



def register_user(data):
	users.add(
		user=data.pop('name'),
		password=data.pop('password'),
		registration_time=int(time.time()),
		**data
	)

def edit_user(user, data):
	for i in data.keys():
		if i == "name" or i == "password" or i == "public_fields":
			pass
		else:
			if isinstance(data[i], bool):
				user[i] = data[i]
			else:
				if data[i].strip() == "":
					if i in user.keys():
						del user[i]
				else:
					user[i] = data[i]

	publicFields = []
	if "public_fields" in data.keys():
		for i in data["public_fields"]:
			if i in data["public_fields"] and i in user.keys():
				publicFields.append(i)
	if len(publicFields) == 0:
		if "public_fields" in user.keys():
			del user["public_fields"]
	else:
		user["public_fields"] = publicFields

	users.save()


@app.route("/api/name_available", methods=["POST"])
def name_available():
	if "/" in request.json['name'] or "\\" in request.json['name']:
		return jsonify({'available': False, 'reason': Errors.forbidden_character.name})
	if users.get(request.json['name']):
		return jsonify({'available': False, 'reason': Errors.name_already_taken.name})
	user_folder = os.path.join("data", request.json['name'].lower().replace(" ", "-"))
	if os.path.exists(user_folder):
		return jsonify({'available': False, 'reason': Errors.creating_folder_error.name})
	return jsonify({'available': True})

@app.route("/api/register", methods=["POST"])
def register():
	if "/" in request.json['name'] or "\\" in request.json['name']:
		return jsonify({'successfully': False, 'reason': Errors.forbidden_character.name})
	for i in request.json.values():
		if len(i.strip()) == 0:
			return jsonify({'successfully': False, 'reason': Errors.forbidden_character.name})
	
	if request.json['name'].lower() == "admin":
		return jsonify({'successfully': False, 'reason': Errors.name_already_taken.name})
	if users.get(request.json['name']):
		return jsonify({'successfully': False, 'reason': Errors.name_already_taken.name})
	try:
		user_folder = os.path.join("data", request.json['name'].lower().replace(" ", "-"))
		if not os.path.exists(user_folder):
			os.makedirs(user_folder)
			with open(os.path.join(user_folder, 'artist.json'), 'w', encoding='utf8') as file:
				file.write(htmlTemplates.atrist_config(request.json['name']))
			with open(os.path.join(user_folder, 'index.html'), 'w', encoding='utf8') as file:
				file.write(htmlTemplates.artist_index(request.json['name']))
		else:
			return jsonify({'successfully': False, 'reason': Errors.creating_folder_error.name})
	except:
		return jsonify({'successfully': False, 'reason': Errors.creating_folder_error.name})

	try:
		register_user(request.json)
		return jsonify({'successfully': True})
	except:
		shutil.rmtree(user_folder)
		return jsonify({'successfully': False, 'reason': Errors.invalid_parameters.name})

def fast_login(user, password):
	data = users.get(user)
	if data:
		if data['password'] == password:
			data['last_online'] = int(time.time())
			users.save()
			return True
	return False

@app.route("/api/login", methods=["POST"])
def login():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	x = BrootForceProtection(request.json['name'], request.json['password'], ip, fast_login)()
	if not x['successfully']:
		x['reason'] = Errors.incorrect_name_or_password.name
	return jsonify(x)

@app.route("/api/reset", methods=["POST"])
def reset():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	x = BrootForceProtection(request.json['user'], request.json['old_password'], ip, fast_login)()
	if x['successfully']:
		user = users.get(request.json['user'])
		user["password"] = request.json['new_password']
		users.save()
		return jsonify({'successfully': True})
	else:
		x['reason'] = Errors.incorrect_name_or_password.name
	return jsonify(x)



@app.route("/api/search", methods=["POST"])
def search():
	def search_track(text):
		final = []
		for track in tracks.data:
			confidence = fuzz.partial_ratio(track['track'].lower(), text.lower())
			if confidence > 80:
				final.append(track)
				continue
			confidence = fuzz.partial_ratio(track['artist'].lower(), text.lower())
			if confidence > 80:
				final.append(track)
				continue
		return final

	def search_user(text):
		final = []
		for user in users.data.keys():
			confidence = fuzz.partial_ratio(user.lower(), text.lower())
			if confidence > 80:
				user_folder_public = user.lower().replace(" ", "-")
				user_folder = os.path.join("data", user_folder_public)
				try:
					with open(os.path.join(user_folder, "artist.json"), 'r', encoding='utf8') as file:
						lines = file.readlines()
						string = "".join(filter(lambda x: not "//" in x, lines)) # remove comments
						string = string.split('=', 1)[1]
						artist_settings = json.loads(string)
						image = os.path.normpath(os.path.join(user_folder_public, artist_settings['image']))
				except:
					image = os.path.normpath(os.path.join(user_folder_public, "../root_/images/people.svg"))
				
				temp = {"user": user, "path": user.lower().replace(" ", "-"), "image": image}
				final.append(temp)
		return final

	def search_genre(text):
		final = []
		for track in tracks.data:
			confidence = fuzz.partial_ratio(track['genre'].lower(), text.lower())
			if confidence > 80:
				final.append(track)
		return final


	if request.json['type'] == "track":
		return jsonify(search_track(request.json['text']))
	elif request.json['type'] == "user":
		return jsonify(search_user(request.json['text']))
	elif request.json['type'] == "genre":
		return jsonify(search_genre(request.json['text']))
	else:
		return "404"


def parse_boolean(value):
	if value == True or value == "true" or value == "True":
		return True
	return False

def make_config(data, files):
	config = {}
	config["track_name"] = data["track_name"]
	config["artist"] = data["artist"]
	config["genre"] = data["genre"]
	config["main_img"] = files["image"].filename
	config["allow_download"] = parse_boolean(data["allow_download"])
	config["download_file"] = files["audio"].filename
	config["audio_preview"] = files["audio"].filename

	config["show_time"] = True
	config["animate_time"] = True

	links = {}
	hosts = ['spotify', 'youtube_music', 'youtube', 'apple_music', 'deezer', 'soundcloud', 'newgrounds']
	for i in hosts:
		if i in data.keys():
			links[i] = data[i]
	if links:
		config['links'] = links

	return config

def edit_config(data, old_data):
	old_data["genre"] = data["genre"]
	old_data["allow_download"] = parse_boolean(data["allow_download"])
	old_data["preview_z"] = parse_boolean(data["preview_z"])
	if "preview_zone" in data.keys():
		old_data["preview_zone"] = list(map(float, data["preview_zone"].split(",")))
	links = {}
	hosts = ['spotify', 'youtube_music', 'youtube', 'apple_music', 'deezer', 'soundcloud', 'newgrounds']
	for i in hosts:
		if i in data.keys():
			links[i] = data[i]
	if links:
		old_data['links'] = links
	return old_data


@app.route('/api/uploader', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.form['artist'], request.form['password'], ip, fast_login)()
		if x['successfully']:
			user_folder = os.path.join("data", request.form['artist'].lower().replace(" ", "-"))
			track_folder = os.path.join(user_folder, request.form['track_name'].lower().replace(" ", "-"))

			if os.path.exists(user_folder):
				if "/" in request.form['track_name'] or "\\" in request.form['track_name']:
					return jsonify({'successfully': False, 'reason': Errors.track_forbidden_character.name})

				if tracks.find(artist=request.form['artist'], track=request.form['track_name']):
					return jsonify({'successfully': False, 'reason': Errors.track_already_exists.name})

				if not os.path.exists(track_folder):
					os.makedirs(track_folder)

					for i in request.files:
						f = request.files[i]

						if f.mimetype.split('/')[0] == 'image':
							image_bytes = BytesIO(f.stream.read())
							blob = image_bytes.read()
							filesize = len(blob)
							if filesize <= 2097152:
								img = Image.open(image_bytes)
								w, h = img.size
								if w <= 1280 and h <= 1280:
									with open(os.path.join(track_folder, f.filename),'wb') as file:
										file.write(blob)
								else:
									shutil.rmtree(track_folder)
									return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})
							else:
								shutil.rmtree(track_folder)
								return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})

						elif f.mimetype.split('/')[0] == 'audio':
							_, extension = os.path.splitext(f.filename)
							if extension == ".mp3":
								audio_bytes = BytesIO(f.stream.read())
								blob = audio_bytes.read()
								filesize = len(blob)
								if filesize <= 10485760:
									metadata = audio_metadata.loads(blob)
									bitrate = metadata.streaminfo.bitrate / 1000
									if bitrate <= 192:
										with open(os.path.join(track_folder, f.filename),'wb') as file:
											file.write(blob)
									else:
										shutil.rmtree(track_folder)
										return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})
								else:
									shutil.rmtree(track_folder)
									return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})
							else:
								shutil.rmtree(track_folder)
								return jsonify({'successfully': False, 'reason': Errors.wrong_file_format.name})


					try:
						config = make_config(request.form.to_dict(), request.files.to_dict())
						with open(os.path.join(track_folder, 'config.json'), 'w', encoding='utf8') as file:
							file.write('config = ' + json.dumps(config, indent=4, ensure_ascii=False))

						with open(os.path.join(track_folder, 'index.html'), 'w', encoding='utf8') as file:
							file.write(htmlTemplates.track_index(request.form['artist'], request.form['track_name'], request.files['image'].filename))
						with open(os.path.join(track_folder, 'embed.html'), 'w', encoding='utf8') as file:
							file.write(htmlTemplates.track_embed())
						
						date = dataparse.parse(request.form['release_date'])
						date_str = f'{str(date.day).zfill(2)}.{str(date.month).zfill(2)}.{date.year}'

						tracks.add(track=request.form['track_name'],
								artist=request.form['artist'],
								genre=request.form['genre'],
								image=request.files['image'].filename,
								date=date_str,
								path=[
									request.form['artist'].lower().replace(" ", "-"),
									request.form['track_name'].lower().replace(" ", "-")
								],
								statistics={"likes": 0, "views": 0}
								)
						
						url = request.form['artist'].lower().replace(" ", "-") + "/" + request.form['track_name'].lower().replace(" ", "-")
						return jsonify({'successfully': True, 'url': url})

					except Exception as e:
						print(e)
						shutil.rmtree(track_folder)
						return jsonify({'successfully': False, 'reason': Errors.invalid_parameters.name})
			
			return jsonify({'successfully': False, 'reason': Errors.creating_folder_error.name})

		else:
			return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})



def delete_track_func(user, track):
	user_folder = os.path.join("data", user.lower().replace(" ", "-"))
	track_folder = os.path.join(user_folder, track.lower().replace(" ", "-"))
	if os.path.exists(track_folder):
		shutil.rmtree(track_folder)

		track_id = tracks.find(artist=user, track=track)
		tracks.delete(track_id)
		return True
	else:
		return False

@app.route('/api/delete_track', methods=['POST'])
def delete_track():
	if request.method == 'POST':
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.json['artist'], request.json['password'], ip, fast_login)()
		if x['successfully']:
			if delete_track_func(request.json['artist'], request.json['track_name']):
				return jsonify({'successfully': True})
			return jsonify({'successfully': False, 'reason': Errors.track_dont_exists.name})
		else:
			return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})


def get_track_info_json(path, other_track_info):
	with open(path, 'r', encoding='utf8') as file:
		lines = file.readlines()
		string = "".join(filter(lambda x: x.strip()[:2] != "//", lines)) # remove comments
		string = string.split('=', 1)[1]
		config = json.loads(string)
		config['date'] = other_track_info['date']
	return config

@app.route('/api/get_track_info', methods=['POST'])
def get_track_info():
	try:
		track = tracks.find(artist=request.json['artist'], track=request.json['track'])
		if track:
			try:
				user_folder = os.path.join("data", request.json['artist'].lower().replace(" ", "-"))
				track_folder = os.path.join(user_folder, request.json['track'].lower().replace(" ", "-"))
				track_inf = tracks.get(track)
				config = get_track_info_json(os.path.join(track_folder, 'config.json'), track_inf)
				return jsonify({'successfully': True, 'config': config})
			except:
				return jsonify({'successfully': False, 'reason': Errors.error_working_files.name})
		else:
			return jsonify({'successfully': False, 'reason': Errors.track_dont_exists.name})
	except:
		return jsonify({'successfully': False, 'reason': Errors.invalid_parameters.name})

@app.route('/api/edit_track', methods=['POST'])
def edit_track_api():
	if request.method == 'POST':
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.form['artist'], request.form['password'], ip, fast_login)()
		if x['successfully']:
			user_folder = os.path.join("data", request.form['artist'].lower().replace(" ", "-"))
			track_folder = os.path.join(user_folder, request.form['track_name'].lower().replace(" ", "-"))

			if os.path.exists(track_folder):
				try:
					track = tracks.find(artist=request.form['artist'], track=request.form['track_name'])
					track_inf = tracks.get(track)
					old_config = get_track_info_json(os.path.join(track_folder, 'config.json'), track_inf)

					config = edit_config(request.form.to_dict(), old_config)
					with open(os.path.join(track_folder, 'config.json'), 'w', encoding='utf8') as file:
						file.write('config = ' + json.dumps(config, indent=4, ensure_ascii=False))
					
					date = dataparse.parse(request.form['release_date'])
					date_str = f'{str(date.day).zfill(2)}.{str(date.month).zfill(2)}.{date.year}'

					track_inf['genre'] = request.form['genre']
					track_inf['date'] = date_str
					
					tracks.save()
					
					url = request.form['artist'].lower().replace(" ", "-") + "/" + request.form['track_name'].lower().replace(" ", "-")
					return jsonify({'successfully': True, 'url': url})

				except Exception as e:
					print(e)
					return jsonify({'successfully': False, 'reason': Errors.invalid_parameters.name})
			
			return jsonify({'successfully': False, 'reason': Errors.error_working_files.name})

		else:
			return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})




@app.route('/api/get_profile_photo', methods=['POST'])
def get_profile_photo():
	try:
		user_folder_public = request.json['artist'].lower().replace(" ", "-")
		user_folder = os.path.join("data", user_folder_public)

		try:
			with open(os.path.join(user_folder, "artist.json"), 'r', encoding='utf8') as file:
				lines = file.readlines()
				string = "".join(filter(lambda x: not "//" in x, lines)) # remove comments
				string = string.split('=', 1)[1]
				artist_settings = json.loads(string)
			
			return jsonify({'successfully': True, 'image': 
				os.path.normpath(os.path.join(user_folder_public, artist_settings['image']))
				})
		except:
			return jsonify({'successfully': True, 'image': 
				os.path.normpath(os.path.join(user_folder_public, "../root_/images/people.svg"))
				})
	except:
		return jsonify({'successfully': False, 'reason': Errors.invalid_parameters.name})

@app.route('/api/change_profile_photo', methods=['POST'])
def change_profile_photo():
	if request.method == 'POST':
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.form['artist'], request.form['password'], ip, fast_login)()
		if x['successfully']:
			user_folder = os.path.join("data", request.form['artist'].lower().replace(" ", "-"))
			try:
				with open(os.path.join(user_folder, "artist.json"), 'r', encoding='utf8') as file:
					lines = file.readlines()
					string = "".join(filter(lambda x: not "//" in x, lines)) # remove comments
					string = string.split('=', 1)[1]
					artist_settings = json.loads(string)

				image_path = os.path.normpath(os.path.join(os.path.abspath(user_folder), artist_settings['image']))

				if 'delete' in request.form.keys():
					artist_settings_image = "../root_/images/people.svg" # default
					if os.path.isfile(image_path):
						os.remove(image_path)
				else:
					f = request.files['image']
					if f.mimetype.split('/')[0] == 'image':
						image_bytes = BytesIO(f.stream.read())
						blob = image_bytes.read()
						filesize = len(blob)
						if filesize <= 2097152:
							img = Image.open(image_bytes)
							w, h = img.size
							if w <= 1280 and h <= 1280:
								if os.path.isfile(image_path):
									os.remove(image_path)
								with open(os.path.join(user_folder, f.filename),'wb') as file:
									file.write(blob)
								artist_settings_image = f.filename
							else:
								return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})
						else:
							return jsonify({'successfully': False, 'reason': Errors.file_is_too_big.name})
					else:
						return jsonify({'successfully': False, 'reason': Errors.wrong_file_format.name})

				with open(os.path.join(user_folder, 'artist.json'), 'w', encoding='utf8') as file:
					file.write(htmlTemplates.atrist_config(
						request.form['artist'],
						artist_settings_image
					))
				with open(os.path.join(user_folder, 'index.html'), 'w', encoding='utf8') as file:
					file.write(htmlTemplates.artist_index(
						request.form['artist'],
						artist_settings_image
					))

				return jsonify({'successfully': True})
			
			except:
				return jsonify({'successfully': False, 'reason': Errors.error_working_files.name})
			
			return jsonify({'successfully': True})
		else:
			return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})


@app.route('/api/get_profile_info', methods=['POST'])
def get_profile_info():
	user = users.get(request.json['user'])
	if user:
		is_admin = False
		if 'role' in user.keys() and user['role'] == 'admin':
			is_admin = True

		path = "/" + request.json['user'].lower().replace(" ", "-")
		return jsonify({'successfully': True, 'is_admin': is_admin, 'path': path})
	else:
		return jsonify({'successfully': False, 'reason': Errors.user_dont_exist.name})

@app.route('/api/get_user_profile', methods=['POST'])
def get_user_profile():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	x = BrootForceProtection(request.json['name'], request.json['password'], ip, fast_login)()
	if x['successfully']:
		user = users.get(request.json['name'])
		if user:
			temp = dict(user)
			del temp['password']
			del temp['registration_time']
			return jsonify({'successfully': True, 'data': temp})
		else:
			return jsonify({'successfully': False, 'reason': Errors.user_dont_exist.name})
	else:
		return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})

@app.route('/api/get_user_profile_public', methods=['POST'])
def get_user_profile_public():
	user = users.get(request.json['user'])
	if user:
		temp = dict(user)
		public_fields = {}
		if "public_fields" in temp.keys():
			for i in temp["public_fields"]:
				try: public_fields[i] = temp[i]
				except: pass
		if "official" in temp.keys():
			public_fields["official"] = temp["official"]
		return jsonify({'successfully': True, "public_fields": public_fields})
	else:
		return jsonify({'successfully': False, 'reason': Errors.user_dont_exist.name})

@app.route('/api/edit_user_profile', methods=['POST'])
def edit_user_profile():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	x = BrootForceProtection(request.json['name'], request.json['password'], ip, fast_login)()
	if x['successfully']:
		user = users.get(request.json['name'])
		if user:
			edit_user(user, request.json)
			return jsonify({'successfully': True})
		else:
			return jsonify({'successfully': False, 'reason': Errors.user_dont_exist.name})
	else:
		return jsonify({'successfully': False, 'reason': Errors.incorrect_name_or_password.name})


@app.route('/api/get_statistic', methods=["POST"])
def get_statistic():
	track_dir = Path(os.path.dirname(request.json['url'])).parts
	clear_track_dir = list(filter(lambda x: x != "\\", track_dir))
	track_id = tracks.find(path=clear_track_dir)
	track = tracks.get(track_id)
	statistic = track['statistics']
	if ('user' in request.json.keys() and 'password' in request.json.keys()):
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.json['user'], request.json['password'], ip, fast_login)()
		if x['successfully']:
			user = users.get(request.json['user'])
			favorites = []
			if 'favorites' in user.keys():
				favorites = user['favorites']
			if os.path.join(*clear_track_dir) in favorites:
				return jsonify({'statistic': statistic, 'liked': True})
	return jsonify({'statistic': statistic})

@app.route('/api/like', methods=["POST"])
def like():
	ip = request.headers.get('X-Forwarded-For', request.remote_addr)
	x = BrootForceProtection(request.json['user'], request.json['password'], ip, fast_login)()
	if x['successfully']:
		track_dir = Path(os.path.dirname(request.json['url'])).parts
		clear_track_dir = list(filter(lambda x: x != "\\", track_dir))
		clear_track_dir_str = os.path.join(*clear_track_dir)
		track_id = tracks.find(path=clear_track_dir)
		statistic = {"likes":0}
		if track_id:
			track = tracks.get(track_id)
			statistic = track['statistics']
		user = users.get(request.json['user'])
		favorites = []
		if 'favorites' in user.keys():
			favorites = user['favorites']
		if clear_track_dir_str in favorites:
			favorites.remove(clear_track_dir_str)
			statistic["likes"] = max(statistic["likes"] - 1, 0)
			event = "unliked"
		else:
			favorites.append(clear_track_dir_str)
			statistic["likes"] += 1
			event = "liked"

		if len(favorites) == 0:
			del user['favorites']
		else:
			user['favorites'] = favorites
		users.save()
		tracks.save()

		return jsonify({'successfully': True, "event": event})
	return jsonify({'successfully': False})

@app.route('/api/get_favorites', methods=['POST'])
def get_favorites():
	def get_favs(user_data):
		favorites = []
		if 'favorites' in user_data.keys():
			favorites = user_data['favorites']
		favorites_new = []
		for i in favorites:
			track_id = tracks.find(path=list(Path(i).parts))
			if track_id:
				track = tracks.get(track_id)
			else:
				track = {'track': "Deleted Track", 'status': 'deleted', 'path': list(Path(i).parts)}
			favorites_new.append(track)
		return favorites_new

	user_data = users.get(request.json['user'])
	if ('password' in request.json.keys()):
		ip = request.headers.get('X-Forwarded-For', request.remote_addr)
		x = BrootForceProtection(request.json['user'], request.json['password'], ip, fast_login)()
		if x['successfully']:
			favs = get_favs(user_data)
			return jsonify({'successfully': True, "favorites": favs})

	if "public_favorites" in user_data:
		if user_data["public_favorites"]:
			favs = get_favs(user_data)
			return jsonify({'successfully': True, "favorites": favs})

	return jsonify({'successfully': False})



def delete_user(user):
	user_folder = os.path.join("data", user.lower().replace(" ", "-"))
	if os.path.exists(user_folder):
		shutil.rmtree(user_folder)
		try:
			users.delete(user)
			return True
		except: None
	return False

@app.route('/api/reset_pwd_html', methods=['GET','POST'])
def reset_pwd_html():
	def get_html():
		args = {'link': ''}
		if 'lang' in request.args.keys():
			args['lang'] = request.args['lang']
		if "url" in request.args.keys():
			args['link'] = request.args['url']

		return htmlTemplates.reset_password(**args)

	html = get_html()
	if 'textMode' in request.args.keys():
		return Response(dedent(html.replace("	", "    ")), mimetype='text/plain')
	else:
		Final_html = '''
			<head><meta name="viewport" content="width=device-width"></head>
			<script>
				function change_lang(lang){
					const args = new URLSearchParams(window.location.search);
					args.set('lang', lang)
					location.search = args.toString()
				}
			</script>
			<a href="javascript:location.search+='&textMode=true'"><button style="font-size:14pt;">Text mode</button></a>
			<div style="float:right;">
				<button onclick="change_lang('en')" style="font-size:14pt;cursor:pointer;">En</button>
				<button onclick="change_lang('ru')" style="font-size:14pt;cursor:pointer;">Ru</button>
			</div>
			<hr>
		'''
		return Final_html + html
		


# Admin
@app.route('/api/admin', methods=['POST'])
def is_admin():
	user = users.get(request.json['user'])
	if user:
		if "role" in user.keys() and user['role'] == "admin":
			ip = request.headers.get('X-Forwarded-For', request.remote_addr)
			x = BrootForceProtection(request.json['user'], request.json['password'], ip, fast_login)()
			if x['successfully']:
				if 'command' in request.json.keys():				
					if request.json['command'] == "get_all_users":
						return jsonify({'successfully': True, 'data': list(users.data.keys())})
					elif request.json['command'] == "get_all_tracks":
						return jsonify({'successfully': True, 'data': list(tracks.data)})
					elif request.json['command'] == "get_all_admins":
						admins = users.find_all(role="admin")
						return jsonify({'successfully': True, 'data': admins})
					elif request.json['command'] == "search_by_email":
						users_arr = users.find_all(email=request.json['email'])
						return jsonify({'successfully': True, 'data': users_arr})
					elif request.json['command'] == "get_user_roles":
						user = users.get(request.json['user_to_get'])
						roles = {}
						if 'role' in user.keys():
							roles['role'] = user['role']
						if 'official' in user.keys():
							roles['official'] = user['official']
						return jsonify({'successfully': True, 'data': roles})
					elif request.json['command'] == "change_role":
						user = users.get(request.json['user_to_change'])
						user['role'] = request.json['new_value']
						users.save()
						return jsonify({'successfully': True, 'user': request.json['user_to_change'], 'role': request.json['new_value']})
					elif request.json['command'] == "change_official":
						user = users.get(request.json['user_to_change'])
						user['official'] = parse_boolean(request.json['new_value'])
						users.save()
						return jsonify({'successfully': True, 'user': request.json['user_to_change'], 'official': parse_boolean(request.json['new_value'])})
					elif request.json['command'] == "delete":
						if request.json['type'] == 'track':
							if delete_track_func(request.json['artist'], request.json['track']):
								return jsonify({'successfully': True, 'deleted': True})
							return jsonify({'successfully': False})
						elif request.json['type'] == 'user':
							if request.json['user_to_delete'] == request.json['user']:
								return jsonify({'successfully': False, 'reason': "you_cant_delete_yourself"})
							if delete_user(request.json['user_to_delete']):
								return jsonify({'successfully': True, 'deleted': True})
							return jsonify({'successfully': False})
					elif request.json['command'] == "get_password":
						user = users.get(request.json['user_to_login'])
						return jsonify({'successfully': True, 'password': user['password']})
					elif request.json['command'] == "reset_password":
						user = users.get(request.json['user_to_reset'])
						return jsonify({'successfully': True, 'user': request.json['user_to_reset'], 'password': user['password']})

				return jsonify({'successfully': True})

	return jsonify({'successfully': False, 'reason': "user_not_admin"})


if __name__ == '__main__':
	# app.run(debug=True)
	app.run(host='0.0.0.0', port='80')
