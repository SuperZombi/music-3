var tmp_th = window.localStorage.getItem('theme')
if(tmp_th){
	if (tmp_th == "dark"){
		darkThemeMq = true
		var l = document.createElement("link")
		l.rel = "stylesheet"
		l.setAttribute("href", "/root_/styles/dark.css");
		document.head.appendChild(l)
	}
	else{
		darkThemeMq = false
	}
}
else{
	darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)").matches
	if (darkThemeMq) {
		var l = document.createElement("link")
		l.rel = "stylesheet"
		l.setAttribute("href", "/root_/styles/dark.css");
		document.head.appendChild(l)
	}
}