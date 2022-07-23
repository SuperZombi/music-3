(function(){
	let el = document.createElement('style');
	el.innerHTML = `
		#preloader{
			position: fixed;
			top: 50%; left: 50%;
			transform: translate(-50%, -50%);
		}
		.lds-dual-ring {
			display: inline-block;
			width: 80px; height: 80px;
		}
		.lds-dual-ring:after {
			content: ""; display: block;
			width: 64px; height: 64px;
			margin: 8px;
			border-radius: 50%;
			border: 6px solid #00B0FF;
			border-color: #00B0FF transparent #00B0FF transparent;
			animation: lds-dual-ring 1.2s linear infinite;
		}
		@keyframes lds-dual-ring {
		  0% { transform: rotate(0deg); }
		  100% { transform: rotate(360deg); }
		}
		`
	document.head.appendChild(el)
	document.body.innerHTML += `
		<div id="preloader">
			<div class="lds-dual-ring"></div>
		</div>`
})()

function parseHTML(html) {
	let temp = html.split("<").filter(n=>n)[0].split(" ")
	let elem = temp[0]
	let atrs = temp.slice(1,)
	atrs[atrs.length-1] = atrs[atrs.length-1].split(">")[0]

	let htmlEl = document.createElement(elem)
	atrs.forEach(atr=>{
		htmlEl.setAttributeNode(parseAtribute(atr))
	})
	return htmlEl;
}
function parseAtribute(string){
	let arr = string.split("=")
	let a = document.createAttribute(arr[0])
	if (arr.length > 1){
		a.value = arr[1].replace(/['"]+/g, '')
	}
	return a;
}

async function load_source(element){
	await new Promise((resolve, reject) => {
		let link = element.src || element.href;
		if (link.includes('fontawesome')){
			document.head.appendChild(element);
		}
		else{
			fetch(link)
				.then((response) => {
					if (response.ok) {
						load_this(response.blob())
					}
					else{
						console.log(`Reloading ${link}`)
						load_source(element)	
					}
				});
			async function load_this(data){
				var data = await data;
				var url = window.URL.createObjectURL(data);
				if (element.src){ element.src = url }
				else if (element.href){ element.href = url }
				document.head.appendChild(element)
				resolve()
			}		
		}
	});
}

function loadApp(imports){
	let array = imports.split('\n').map(e=>e.trim()).filter(n=>n);
	async function next(arr) {
		if (arr.length) {
			let el = parseHTML(arr.shift())
			if(el.hasAttribute("required")){
				await load_source(el)
			}
			else{
				load_source(el)
			}
			next(arr)
		}
	}
	next(array);
}
