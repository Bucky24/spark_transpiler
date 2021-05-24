class Api {
    constructor() {
        this.apis = {
            post: {},
			get: {},
        };
    }

    post(name, cb) {
        this.apis.post[name] = cb;
    }

	get(name, cb) {
        this.apis.get[name] = cb;
    }

    async execute(method, name, params) {
        if (!this.apis[method]) {
            throw new Error(`Unknown method ${method}`);
        }

        if (!this.apis[method][name]) {
            throw new Error(`Unknown api ${method} ${name}`);
        }

        return await this.apis[method][name](params);
    }
};

const api = new Api();

module.exports = {
	print: (...args) => {
		console.log(...args);
	},
	Api: api,
};