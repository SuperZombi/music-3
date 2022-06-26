(function load_page(){
if (typeof header !== 'undefined' && typeof body !== 'undefined'){
	document.body.innerHTML += header
	document.body.innerHTML += body

	setTimeout(function(){document.body.style.transition = "1s"}, 500)
	main()
	document.getElementById("preloader").style.display = "none"
}
else{
	setTimeout(function(){load_page()}, 500)
}
})()

function goToLogin(){
	let url = window.location.pathname;
	let login = new URL("/account/login", window.location.href);
	login.searchParams.append('redirect', url);
	window.location.href = decodeURIComponent(login.href)
}

function main(){
	local_storage = { ...localStorage };
	if (local_storage.userName && local_storage.userPassword){
		let data = {
			'user': local_storage.userName,
			'password': local_storage.userPassword
		}
		fetch('/api/admin', {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {'Content-Type': 'application/json'}
		}).then(answer => answer.json()).then(answer => {
			if (answer.successfully){
				document.body.addEventListener('keydown', event=>{typeInConsole(event)})
				document.body.addEventListener('keyup', event=>{keyboardUp(event)})
				document.getElementById('admin_console').style.display = "block";
			}
			else{
				window.location.href = new URL("/403", window.location.href)
			}
		})
	}
	else{
		goToLogin()
	}
}

var ctrlPressed = false
function keyboardUp(event){
	if (event.key == "Control"){
		ctrlPressed = false;
	}
}
function typeInConsole(event){
	if (consoleFocused){
		if (event.ctrlKey){
			ctrlPressed = true;
		}
		else if (event.keyCode==8){
			let last_element = document.getElementById("console").querySelector(".consolePositioner").previousSibling
			if (last_element.className != "admin"){
				document.getElementById("console").querySelector(".consolePositioner").previousSibling.remove()
			}
		}
		else if (event.keyCode==13){
			exec_console_command()
		}
		else if (event.key.length == "1"){
			if (!ctrlPressed){
				let elem = document.createElement('a')
				elem.innerHTML = event.key
				document.getElementById("console").insertBefore(elem, document.getElementById("console").lastChild);
			}
		}
	}
}

var consoleFocused = false;
function focusConsole(event){
	let console_ = document.getElementById("console")
	let unfocused = event.path.every(function(e) {
		if (e == console_) return false
		else return true
	})
	if (unfocused){
		consoleFocused = false;
		Array.from(console_.querySelectorAll('.consolePositioner')).forEach(e=>e.remove())
	}
	else{
		consoleFocused = true;
		if (console_.lastChild.className != "consolePositioner"){
			console_.innerHTML += "<a class='consolePositioner'>|</a>"
		}
	}
}
function clearConsole(){
	document.getElementById("console").innerHTML = '<a class="admin">admin></a>'
}

function make_something_with(type, ...args){
	clearConsole()
	args.forEach((e, index)=>{
		if (index == args.length - 1){
			document.getElementById("console").innerHTML += `<a class="custom_command">${e}</a>`
		}
		else{
			document.getElementById("console").innerHTML += `<a class="custom_command" style="margin-right:10px">${e}</a>`
		}
	})
	document.getElementById("console").innerHTML += " > "

	let span = document.createElement('span')
	span.className = "select_list"
	let comand_list = [];
	if (type == "user"){
		comand_list = ['Login under', 'Delete', 'Roles', 'Reset password', 'Cancel']
	}
	else if (type == "track"){
		comand_list = ['Delete', 'Cancel']
	}
	Array.from(comand_list).forEach(command =>{
		let element = document.createElement('a')
		element.className = "clickable_element"
		element.innerHTML = command
		element.setAttribute("onclick","do_with_event('"+command+"');");
		span.appendChild(element)
	})
	document.getElementById("console").appendChild(span)
}
function change_role_event(event){
	document.getElementById("console").querySelector('.all_roles').remove()
	document.getElementById("console").querySelector('br').remove()
	document.getElementById("console").querySelector(".consolePositioner").previousSibling.remove()
	document.getElementById("console").querySelector(".consolePositioner").remove()
	document.getElementById("console").innerHTML += `<a class="command">${event}</a>`
}
function do_with_event(event){
	if (event == 'Cancel'){
		clearConsole()
	}
	else if (event == "Role" || event == "Official"){
		document.getElementById("console").querySelector(".consolePositioner").previousSibling.remove()
		document.getElementById("console").querySelector(".consolePositioner").remove()

		document.getElementById("console").innerHTML += `<a class="command">${event}</a> > `
		let select_arr = []
		if (event == "Official"){
			select_arr = ["true", "false"]
		}
		else if (event == "Role"){
			select_arr = ["user", "admin"]
		}
		let span = document.createElement('span')
		span.className = "select_list"
		Array.from(select_arr).forEach(command =>{
			let element = document.createElement('a')
			element.className = "clickable_element"
			element.innerHTML = command
			element.setAttribute("onclick","change_role_event('"+command+"');");
			span.appendChild(element)
		})
		document.getElementById("console").appendChild(span)
	}
	else if (event == "Roles"){
		document.getElementById("console").querySelector(".consolePositioner").previousSibling.remove()
		document.getElementById("console").querySelector(".consolePositioner").remove()

		fetch('/api/admin', {
			method: 'POST',
			body: JSON.stringify({
				'user': local_storage.userName,
				'password': local_storage.userPassword,
				'command': "get_user_roles",
				'user_to_get': document.getElementById("console").querySelector(".custom_command").innerText
			}), headers: {'Content-Type': 'application/json'}
		}).then(answer => answer.json()).then(answer => {
			try{document.getElementById("console").querySelector(".consolePositioner").remove()}catch{}
			if (answer.successfully){
				document.getElementById("console").innerHTML += `<a class="all_roles">${JSON.stringify(answer.data)}<a><br>`

				let span = document.createElement('span')
				span.className = "select_list"
				Array.from(['Official', 'Role', 'Cancel']).forEach(command =>{
					let element = document.createElement('a')
					element.className = "clickable_element"
					element.innerHTML = command
					element.setAttribute("onclick","do_with_event('"+command+"');");
					span.appendChild(element)
				})
				document.getElementById("console").appendChild(span)
			}
			else{
				document.getElementById("console").innerHTML += 'Error'
			}
			if (document.getElementById("console").lastChild.className != "consolePositioner"){
				document.getElementById("console").innerHTML += "<a class='consolePositioner'>|</a>"
			}
		})
	}
	else{
		document.getElementById("console").querySelector(".consolePositioner").previousSibling.remove()
		document.getElementById("console").querySelector(".consolePositioner").remove()
		document.getElementById("console").innerHTML += `<a class="command">${event}</a>`
	}
}


var search_showed = false;
function doFastCommand(element){
	function send(command, type){
		let data = {
			'user': local_storage.userName,
			'password': local_storage.userPassword,
			'command': command
		}
		fetch('/api/admin', {
			method: 'POST',
			body: JSON.stringify(data),
			headers: {'Content-Type': 'application/json'}
		}).then(answer => answer.json()).then(answer => {
			if (answer.successfully){
				clearConsole()
				document.getElementById("console").innerHTML += `<a class="custom_command">${command}</a>` + "<br>"

				let span = document.createElement('span')
				span.className = "select_list"
				answer.data.forEach(el =>{
					let element = document.createElement('a')
					element.className = "clickable_element"
					if (type == "user"){
						element.innerHTML = el
						element.setAttribute("onclick","make_something_with('"+type+"', '"+el+"');");
					}
					else if (type == "track"){
						element.innerHTML = `[${el.track} | ${el.artist}]`
						element.setAttribute("onclick","make_something_with('"+type+"', '"+el.track+"', '"+el.artist+"');");
					}
					span.appendChild(element)
				})
				document.getElementById("console").appendChild(span)
			}
		})
	}

	if (element.name == "get_all_tracks"){
		send("get_all_tracks", 'track')
	}
	else if (element.name == "get_all_users"){
		send("get_all_users", 'user')
	}
	else if (element.name == "get_all_admins"){
		send("get_all_admins", 'user')
	}
	else if (element.name == "show_search"){
		if (!search_showed){
			search_showed = true;
			element.checked = true;
			document.getElementById('search_menu').style.display = "block"
		}
		else{
			search_showed = false;
			element.checked = false;
			document.getElementById('search_menu').style.display = "none"
		}
	}
	else if (element.name == "search"){
		let search_type = Array.from(document.querySelectorAll("input[name=search_type]")).filter(e=>e.checked)[0].value
		let search_text = document.querySelector("input[name=search_value]").value

		if (search_type && search_text){
			let data = {
				'type': search_type,
				'text': search_text
			}
			fetch('/api/search', {
				method: 'POST',
				body: JSON.stringify(data),
				headers: {'Content-Type': 'application/json'}
			}).then(answer => answer.json()).then(answer => {
				clearConsole()
				document.getElementById("console").innerHTML += `<a class="custom_command">Search ${search_type}</a>` + "<br>"

				if (answer.length == 0){
					document.getElementById("console").innerHTML += "Nothing Found"
				}
				else{
					let span = document.createElement('span')
					span.className = "select_list"
					answer.forEach(el =>{
						let element = document.createElement('a')
						element.className = "clickable_element"
						if (search_type == "user"){
							element.innerHTML = el.user
							element.setAttribute("onclick","make_something_with('"+search_type+"', '"+el.user+"');");
						}
						else if (search_type == "track"){
							element.innerHTML = `[${el.track} | ${el.artist}]`
							element.setAttribute("onclick","make_something_with('"+search_type+"', '"+el.track+"', '"+el.artist+"');");
						}
						span.appendChild(element)
					})
					document.getElementById("console").appendChild(span)
				}
			})	
		}
	}
}




function exec_console_command(){
	let object = document.getElementById("console").querySelectorAll(".custom_command")
	let array = []
	Array.from(object).forEach(e=>{
		array.push(e.innerText)
	})
	let command = document.getElementById("console").querySelectorAll(".command")
	let command_array = []
	Array.from(command).forEach(e=>{
		command_array.push(e.innerText.toLowerCase())
	})

	clearConsole()

	if (array.length == 1){
		type = "user"
	}
	else if (array.length == 2){
		type = "track"
	}

	let do_after = function(){}
	let other_data = {};
	if (command_array.length == 1){
		command = command_array[0]
		if (command == 'delete'){
			if (type == "track"){
				other_data = {
					'artist': array[1],
					'track': array[0]
				}
			}
			else if (type == "user"){
				other_data = {
					'user_to_delete': array[0]
				}
			}
		}
		else if (command == 'login under'){
			command = 'get_password';
			other_data = {
				'user_to_login': array[0]
			}
			do_after = function(answer){
				if (answer.successfully){
					localStorage.setItem('userName', array[0])
					localStorage.setItem('userPassword', answer.password)
					let url = window.location.pathname;
					let login = new URL("/account/", window.location.href);
					window.location.href = decodeURIComponent(login.href)
				}
			}
		}
		else if (command == "reset password"){
			command = "reset_password"
			other_data = {
				'user_to_reset': array[0]
			}
			do_after = function(answer){
				if (answer.successfully){
					clearConsole()
					let url = `/account/login?user=${answer.user}&old=${answer.password}#reset`

					let element = document.createElement('a')
					element.className = "clickable_element"
					element.innerHTML = url
					element.setAttribute("onmousedown","copy_url(event, '"+url+"');");
					document.getElementById("console").appendChild(element)
				}
			}
		}
	}
	else{
		command = "change_" + command_array[0]
		other_data = {
			'user_to_change': array[0],
			'new_value': command_array[1]
		}
	}


	console.log(array, command)

	fetch('/api/admin', {
		method: 'POST',
		body: JSON.stringify({
			'user': local_storage.userName,
			'password': local_storage.userPassword,
			'command': command,
			'type': type,
			...other_data
		}),
		headers: {'Content-Type': 'application/json'}
	}).then(answer => answer.json()).then(answer => {
		document.getElementById("console").innerHTML += JSON.stringify(answer)
		do_after(answer)
	})
}



function copyToClipboard(text) {
	const elem = document.createElement('textarea');
	elem.value = text;
	document.body.appendChild(elem);
	elem.select();
	document.execCommand('copy');
	document.body.removeChild(elem);
}
function copy_url(event, url){
	if (event.which == 2){
		window.open(url, '_blank');
	}
	else{
		let link = new URL(url, window.location.href)
		copyToClipboard(decodeURI(link.href))
		Array.from(document.getElementById("console").querySelectorAll('.consolePositioner')).forEach(e=>e.remove())
		document.getElementById("console").innerHTML += `<br>${LANG.copied}`
	}
}