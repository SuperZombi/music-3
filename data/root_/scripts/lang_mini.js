if (window.localStorage.getItem('lang')){
	language = window.localStorage.getItem('lang')
}
else{
	language = window.navigator.language.substr(0, 2)
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
			}
			else{
				retry_count++;
				if (retry_count > 5){
					var l = document.createElement("script")
					l.setAttribute("src", `/root_/Langs/EN.json`);
					load_source(l)
				}
				else{
					executeIfFileExist()
				}
			}
		}
	}
	xhr.send();
})()