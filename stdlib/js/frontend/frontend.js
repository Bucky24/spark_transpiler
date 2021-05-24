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
	constructor(...args) {
		if (args.length === 3) {
			const [ tag, attrs, children ] = args;
			this.tag = tag;
			this.attrs = attrs;
			this.children = children;
		} else if (args.length === 2) {
			const [ attrs, children ] = args;
			this.tag = null;
			this.attrs = attrs;
			this.children = children;
		}
	}
	
	async render() {
		if (!this.tag) {
			// in this case we're probably rendering a child class. It should have
			// its own render function, but in case we get here, just don't do anything
			return;
		}
		const elem = document.createElement(this.tag);
		
		if (this.attrs) {
			for (const key in this.attrs) {
				let val = this.attrs[key];
				if (typeof val === "object") {
					val = val.render();
				}

				if (key.startsWith("on")) {
					const event = key.substr(2).toLowerCase();
					elem.addEventListener(event, val);
				} else {
					elem.setAttribute(key, val);
				}
			}
		}
		
		const renderChild = async (child) => {
			if (typeof child == "string") {
				return document.createTextNode(child);
			} else if (Array.isArray(child)) {
				const resultMap = [];
				for (const entry of child) {
					const result = await renderChild(entry);
					resultMap.push(result);
				}
				child = resultMap;
			} else if (child instanceof Node) {
				return child;
			} else if (typeof child == "object") {
				// it's probably an instance of a component
				const result = await child.render();
				// recurse the render
				return renderChild(result);
			}
			
			return child;
		}
		
		if (this.children) {
			for (const child of this.children) {
				const childResult = await renderChild(child);
				if (Array.isArray(childResult)) {
					childResult.forEach((result) => {
						elem.appendChild(result);
					})
				} else {
					elem.appendChild(childResult);
				}
			}
		}
		
		return elem;
	}
}

class Variable {
	constructor(initialValue) {
		this.value = initialValue;
	}

	get() {
		return this.value;
	}

	set(value) {
		this.value = value;
	}
}

let mainComponent = null;

async function render(component) {
	mainComponent = component;
	const holder = document.getElementById("app");
	const element = await component.render();
	holder.innerHTML = "";
	holder.appendChild(element);
}

async function rerender() {
	if (mainComponent) {
		await render(mainComponent);
	}
}