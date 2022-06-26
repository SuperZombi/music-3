(function load_page(){
if (typeof header !== 'undefined' && typeof body !== 'undefined'){
	document.title = `Zombi Music - ${LANG.support_title}`
	document.body.innerHTML += header
	document.body.innerHTML += body
	darking_images()
	main()

	setTimeout(function(){document.body.style.transition = "1s"}, 500)
	document.getElementById("preloader").style.display = "none"
}
else{
	setTimeout(function(){load_page()}, 500)
}
})()

function darking_images(){
	var tmp_ = document.getElementById("support")
	if (tmp_){
		tmp_2 = tmp_.getElementsByTagName("img")
		Object.keys(tmp_2).forEach(function(e){
			try_dark(tmp_2[e])
		})
	}
}

function main(){
	if (document.getElementById('myAccount').getElementsByTagName('img')[0].src.split('.').pop() == "svg"){
		try_dark(document.getElementById('myAccount').getElementsByTagName('img')[0])
	}
}