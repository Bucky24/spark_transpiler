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

async function renderChild(child) {
	if (typeof child == "string" || typeof child == "boolean" || typeof child == "number") {
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
		// make sure the child is aware of its own element (this may not have happened if it's a component instance that has its own render fn)
		// recurse the render
		const finalResult = await renderChild(result);
		child.setElem(finalResult);
		return finalResult;
	}
	
	return child;
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

	setElem(newElem) {
		this.elem = newElem;
	}

	async rerender() {
		if (!this.elem) {
			console.error("Cannot re-render a Component that has no element");
		}

		const parent = this.elem.parentNode;
		const oldNode = this.elem;
		await renderChild(this);
		parent.replaceChild(this.elem, oldNode);
	}
	
	async render() {
		if (!this.tag) {
			// in this case we're probably rendering a child class. It should have
			// its own render function, but in case we get here, just don't do anything
			return;
		}
		this.elem = document.createElement(this.tag);
		
		if (this.attrs) {
			for (const key in this.attrs) {
				let val = this.attrs[key];
				if (typeof val === "object") {
					val = val.render();
				}

				if (key.startsWith("on")) {
					const event = key.substr(2).toLowerCase();
					this.elem.addEventListener(event, val);
				} else {
					this.elem.setAttribute(key, val);
				}
			}
		}

		if (this.children) {
			for (const child of this.children) {
				const childResult = await renderChild(child);
				if (Array.isArray(childResult)) {
					childResult.forEach((result) => {
						this.elem.appendChild(result);
					})
				} else {
					this.elem.appendChild(childResult);
				}
			}
		}

		return this.elem;
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

function getHelper(obj, pathList, soFar) {
	const segment = pathList.shift();
	if (obj[segment] !== undefined) {
		const result = obj[segment];
		if (pathList.length === 0) {
			return result;
		} else {
			return getHelper(result, pathList, [...soFar, segment]);
		}
	}

	throw new Error(`Could not find ${soFar.join('.')}.${segment}`);
}

class State {
	static state = {}
	static doingRerender = false

	static init(newState) {
		State.state = newState;
	}

	static get(path) {
		return getHelper(State.state, path.split("."), []);
	}

	static set(path, value) {
		const pathList = path.split(".");
		if (pathList.length === 1) {
			State.state[path] = value;
			return;
		}
		const lastEntry = pathList.pop();
		const obj = getHelper(State.state, pathList, []);
		obj[lastEntry] = value;

		if (!State.doingRerender) {
			State.doingRerender = true;
			// hold for 1 ms. This will pop the rerender to a different async thread, meaning additional state updates can finish
			setTimeout(() => {
				State.doingRerender = false;
				rerender();
			}, 1);
		}
	}
}

let mainComponent = null;

async function render(component) {
	mainComponent = component;
	const holder = document.getElementById("app");
	const element = await renderChild(component);
	holder.innerHTML = "";
	holder.appendChild(element);
}

async function rerender() {
	if (mainComponent) {
		await render(mainComponent);
	}
}