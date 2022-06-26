const urlSearchParams = new URLSearchParams(window.location.search);
const params = Object.fromEntries(urlSearchParams.entries());

/* Theme */
if (params.theme){
	if (params.theme == "dark"){
		darkThemeMq = true
		var l = document.createElement("link")
		l.rel = "stylesheet"
		l.setAttribute("href", "../../root_/styles/dark.css");
		l.setAttribute("id", "dark_file");
		document.head.appendChild(l)
	}
	else{
		darkThemeMq = false
	}
}
else{
	darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)").matches
	if (darkThemeMq) {
		darkThemeMq = true
		var l = document.createElement("link")
		l.rel = "stylesheet"
		l.setAttribute("href", "../../root_/styles/dark.css");
		document.head.appendChild(l)
	}
	else{
		darkThemeMq = false
	}
}


/* Lang */
if (params.lang){
	language = params.lang
}
else{
	language = window.navigator.language.substr(0, 2)
}
(function executeIfFileExist() {
	var src = `../../root_/Langs/${language.toUpperCase()}.json`;
	var xhr = new XMLHttpRequest()
	xhr.open('HEAD', src, true)
	xhr.onreadystatechange = function() {
		if (this.readyState === this.DONE) {
			if (xhr.status==200){
				var l = document.createElement("script")
				l.setAttribute("src", `../../root_/Langs/${language.toUpperCase()}.json`);
				document.head.appendChild(l);
			}
			else{
				var l = document.createElement("script")
				l.setAttribute("src", `../../root_/Langs/EN.json`);
				document.head.appendChild(l);
			}
		}
	}
	xhr.send();
})()


/* Border radius */
if (params.round){
	roundPage = (params.round === 'true');
}
else{
	roundPage = true;
}