import os
import shutil
server_current = "C:\\Users\\Ростислав\\Downloads\\zombi-music-server"
server_updates = "C:\\Users\\Ростислав\\Downloads\\music-2-main"

for dname, dirs, files in os.walk(server_updates):
	for fname in files:
		fpath = os.path.join(dname, fname)

		rel = os.path.relpath(fpath, server_updates)
		new = os.path.join(server_current, rel)

		shutil.move(fpath, new)

shutil.rmtree(server_updates)