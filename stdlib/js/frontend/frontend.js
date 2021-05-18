class Component {
	constructor(tag, children) {
		this.tag = tag;
		this.children = children;
	}
	
	render() {
		const elem = document.createElement(this.tag);
		
		if (this.children) {
			for (const child of this.children) {
				if (typeof child == "string") {
					elem.appendChild(child);
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