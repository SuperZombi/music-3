if (location.hash){
	language = location.hash.split("#")[1]
}
else if (window.localStorage.getItem('lang')){
	language = window.localStorage.getItem('lang')
	location.hash = language
}
else{
	language = window.navigator.language.substr(0, 2)
	location.hash = language
}

var retry_count = 0;
(function executeIfFileExist() {
	var src = `/root_/Langs/${language.toUpperCase()}.json`;
	var xhr = new XMLHttpRequest()
	xhr.open('HEAD', src, true)
	xhr.onload = function() {
		if (this.readyState === this.DONE) {
			if (xhr.status==200){
				var l = document.createElement("script")
				l.setAttribute("src", `/root_/Langs/${language.toUpperCase()}.json`);
				load_source(l)
				window.localStorage.setItem('lang', language);
			}
			else{
				retry_count++;
				if (retry_count > 5){
					var l = document.createElement("script")
					l.setAttribute("src", `/root_/Langs/EN.json`);
					load_source(l)
					var th = location.hash.split("#")[2]
					if (typeof th === 'undefined'){
						location.hash = "en"
					}
					else{
						location.hash = `#en#${th}`
					}
				}
				else{
					executeIfFileExist()
				}
			}
		}
	}
	xhr.send();
})()