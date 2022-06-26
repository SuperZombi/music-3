def track_index(artist, track, image):
	return f'''<!DOCTYPE html><html><head>
	<title>Zombi Music</title>
	<meta name="viewport" content="width=device-width"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="shortcut icon" href="../../root_/images/logo2.png" type="image/png">
	<!-- og:zone -->
	<meta property="og:image" content="{image}">
	<meta property="og:title" content="{artist} - {track}">
	<meta property="og:description" content="Zombi Music">
	<meta property="og:site_name" content="zombi.music">
	<meta property='og:type' content="music.song">
	<script src="../../root_/scripts/App.js" defer onload='loadApp(`
		<script src="../../root_/scripts/lang.js"></script>
		<link rel="stylesheet" href="../../root_/styles/main.css">
		<link rel="stylesheet" href="../../root_/styles/ripple.css">
		<link rel="stylesheet" href="../../root_/styles/fontawesome/css/all.min.css">
		<script src="../../root_/scripts/theme.js"></script>
		<script src="config.json"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/2.0.4/wavesurfer.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/2.0.4/plugin/wavesurfer.regions.min.js"></script>
		<script src="../../root_/htmls/header.html"></script>
		<script src="../../root_/htmls/body.html"></script>
		<script src="../../root_/htmls/footer.html"></script>
		<script src="../../root_/scripts/main.js"></script>
	`)'></script>
	</head><body></body></html>'''

def track_embed():
	return f'''<!DOCTYPE html><html><head>
	<title>Zombi Music</title>
	<meta name="viewport" content="width=device-width">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<script src="../../root_/scripts/App.js" defer onload='loadApp(`
		<link rel="stylesheet" href="../../root_/styles/main.css">
		<script src="../../root_/scripts/parse_params.js"></script>
		<link rel="stylesheet" href="../../root_/styles/embed.css">
		<link rel="stylesheet" href="../../root_/styles/fontawesome/css/all.min.css">
		<script src="config.json"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/2.0.4/wavesurfer.min.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/wavesurfer.js/2.0.4/plugin/wavesurfer.regions.min.js"></script>
		<script src="../../root_/htmls/embed.html"></script>
		<script src="../../root_/scripts/embed.js"></script>
	`)'></script>
	</head><body></body></html>'''

def atrist_config(name, image="../root_/images/people.svg"):
	return "ARTIST = {" + f'''"name": "{name}", "image": "{image}"''' + "}"

def artist_index(name, image="../root_/images/people.svg"):
	return f'''<!DOCTYPE html><html><head>
	<title>Zombi Music</title>
	<meta name="viewport" content="width=device-width"><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<link rel="shortcut icon" href="../root_/images/logo2.png" type="image/png">
	<!-- og:zone -->
	<meta property="og:image" content="{image}">
	<meta property="og:title" content="{name}">
	<meta property="og:description" content="Artist">
	<meta property="og:site_name" content="zombi.music">
	<script src="../root_/scripts/App.js" defer onload='loadApp(`
		<script src="../root_/scripts/lang.js"></script>
		<link rel="stylesheet" href="../root_/styles/fontawesome/css/all.min.css">
		<link rel="stylesheet" href="../root_/styles/main.css">
		<script src="../root_/scripts/theme.js"></script>
		<script src="artist.json"></script>
		<script src="../root_/htmls/header.html"></script>
		<script src="../root_/htmls/body_artist.html"></script>
		<script src="../root_/htmls/footer.html"></script>
		<script src="../root_/scripts/artist.js"></script>
	`)'></script>
	</head><body></body></html>'''
