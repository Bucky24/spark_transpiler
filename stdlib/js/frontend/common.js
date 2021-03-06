function print(...args) {
	console.log(...args);
}

const Api = {
	post: (name, args) => {
		const url = "/api/" + name;

		var xhttp = new XMLHttpRequest();
		xhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				console.log(this.responseText);
			}
		};
		xhttp.open("POST", url, true);
		xhttp.send(JSON.stringify(args));
	},
	get: (name, args) => {
		const url = "/api/" + name;

		const argPairs = Object.keys(args).map((key) => {
			const value = args[key];
			return `${key}=${encodeURIComponent(value)}`;
		});

		const params = argPairs.join("&");

		const fullUrl = `${url}?${params}`;

		return new Promise((resolve, reject) => {
			const xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if (this.readyState == 4 && this.status == 200) {
					let result = this.responseText;
					if (result.startsWith("{") || result.startsWith("[")) {
						result = JSON.parse(result);
					}
					resolve(result);
				}
			};
			xhttp.open("GET", fullUrl, true);
			xhttp.send(JSON.stringify(args));
		});
	},
}