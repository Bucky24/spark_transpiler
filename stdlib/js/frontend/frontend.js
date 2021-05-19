class Style {
	constructor(attrs) {
		this.attrs = attrs;
	}
	
	render() {
		const attrList = Object.keys(this.attrs).map((key) => {
			let value = this.attrs[key];
			key = key.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`);
			return `${key}: ${value}`;
		})
		return attrList.join("; ");
	}
}

class Component {
	constructor(tag, attrs, children) {
		this.tag = tag;
		this.attrs = attrs;
		this.children = children;
	}
	
	render() {
		const elem = document.createElement(this.tag);
		
		if (this.attrs) {
			for (const key in this.attrs) {
				let val = this.attrs[key];
				if (typeof val === "object") {
					val = val.render();
				}
				
				elem.setAttribute(key, val);
			}
		}
		
		if (this.children) {
			for (const child of this.children) {
				if (typeof child == "string") {
					elem.innerHTML += child;
				}
			}
		}
		
		return elem;
	}
}

function render(component) {
	const holder = document.getElementById("app");
	const element = component.render();
	holder.innerHTML = "";
	holder.appendChild(element);
}