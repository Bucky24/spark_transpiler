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

    async execute(method, name, params, serverCookies) {
        if (!this.apis[method]) {
            throw new Error(`Unknown method ${method}`);
        }

        if (!this.apis[method][name]) {
            throw new Error(`Unknown api ${method} ${name}`);
        }

        let cookies = {};
        const requestObj = {
            setSession: (data) => {
                const buffer = Buffer.from(JSON.stringify(data));
                const encoded = buffer.toString("base64");
                cookies.session = {
                    value: encoded,
                    // needs to change
                    timeout: 1626225436000,
                };
            },
            getSession: () => {
                const sessionCookie = serverCookies['session'];
                if (!sessionCookie) {
                    return null;
                }
                const buffer = Buffer.from(sessionCookie, 'base64');
                const encoded = buffer.toString('utf8');
                const data = JSON.parse(encoded);
                return data;
            }
        }

        const result = await this.apis[method][name](params, requestObj);

        return {
            result,
            cookies,
        };
    }
};

const api = new Api();

module.exports = {
	print: (...args) => {
		console.log(...args);
	},
	Api: api,
};