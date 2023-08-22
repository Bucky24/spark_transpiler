const http = require("http");
const path = require("path");
const fs = require("fs");
// required because we use Api below
const { Api } = require('./stdlib_js_backend_common.js');

const frontendFiles = {};

function processDir(dir) {
    const paths = fs.readdirSync(dir);

    for (const pathSection of paths) {
        if (pathSection === "stdlib_js_backend_webapp.tmpl.js") {
            // don't need to import ourselves
            continue;
        }
        const fullPath = path.join(dir, pathSection);
        const stats = fs.statSync(fullPath);
        if (stats.isDirectory()) {
            processDir(fullPath);
        } else {
            const isBackend = pathSection.includes("backend");
            const isFrontend = pathSection.includes("frontend");
            if (isFrontend) {
                const tempPath = fullPath.replace(dir, "./");
                frontendFiles[tempPath] = fullPath;
            } else if (isBackend) {
                require(fullPath);
            }
        }
    }
}

processDir(__dirname);

const frontendFileKeys = Object.keys(frontendFiles);

const hostname = "localhost";
const port = 3000;

function serveFile(response, file) {
    const fullPath = path.resolve(__dirname, file);
    const stat = fs.statSync(fullPath);

    let type = "text/plain";
    if (file.endsWith(".html")) {
        type = "text/html";
    } else if (file.endsWith(".js")) {
        type = "text/js";
    }

    response.writeHead(200, {
        'Content-Type': type,
        'Content-Length': stat.size
    });

    const readStream = fs.createReadStream(fullPath);
    readStream.pipe(response);
}

function parseHeaders(headers) {
    const headerPairs = {};
    let key = null;
    for (let i=0;i<headers.length;i++) {
        const entry = headers[i];
        if (i % 2 === 0) {
            key = entry;
        } else {
            if (!headerPairs[key]) {
                headerPairs[key] = [];
            }
            headerPairs[key].push(entry);
        }
    }
    return headerPairs;
}

function parseCookies(cookieList) {
    if (!cookieList) {
        return {};
    }
    const cookies = cookieList.reduce((list, string) => {
        return [
            ...list,
            ...string.split(";"),
        ];
    }, []);
    const cookieObj = cookies.reduce((obj, string) => {
        let [key, value] = string.split("=");
        key = key.trim();
        value = decodeURIComponent(value);
        return {
            ...obj,
            [key]: value,
        };
    }, {});

    return cookieObj;
}

const server = http.createServer((req, res) => {
    let body = "";
    req.on('readable', function() {
        const read = req.read();
        if (read) {
            body += read;
        }
    });
    req.on('end', async function() {
        // cut off the first slash
        req.url = req.url.substr(1);
        if (req.url === "") {
            res.setHeader('Access-Control-Allow-Credentials', true);
            serveFile(res, "stdlib_js_frontend_index.html");
        } else if (frontendFileKeys.includes(req.url)) {
            serveFile(res, frontendFiles[req.url]);
        } else if (req.url === "updateTime") {
            const updatePath = path.join(__dirname, "__update_time__");
            if (!fs.existsSync(updatePath)) {
                res.writeHead(200);
                res.write('0');
                res.end();
            } else {
                const updateTime = fs.readFileSync(path.join(__dirname, "__update_time__"));
                res.writeHead(200);
                res.write(updateTime);
                res.end();
            }
        } else if (req.url.startsWith("api/")) {
            const headers = parseHeaders(req.rawHeaders);
            const cookieObj = parseCookies(headers['Cookie']);
            const url = req.url.substr(4);
            const parts = url.split("?");
            const apiName = parts[0];
            const paramStr = parts[1] || "";
            const paramList = paramStr.split("&");
            let params = paramList.reduce((obj, pair) => {
                let [key, value] = pair.split("=");
                value = decodeURIComponent(value);
                return {
                    ...obj,
                    [key]: value,
                };
            }, {});
            if (body !== "") {
                const bodyJson = JSON.parse(body);
                params = {
                    ...params,
                    ...bodyJson,
                };
            }
            try {
                const { result, cookies } = await Api.execute(req.method.toLowerCase(), apiName, params, cookieObj);
                res.setHeader('Access-Control-Allow-Credentials', true);
                Object.keys(cookies).forEach((cookie) => {
                    const cookieData = cookies[cookie];
                    let resultCookie = `${cookie}=${encodeURIComponent(cookieData.value)}`;
                    if (cookieData.timeout) {
                        const date = new Date(cookieData.timeout);
                        resultCookie += `; Expires=${date.toISOString()};`;
                    }
                    res.setHeader('Set-Cookie', resultCookie);
                });
                res.writeHead(200);
                if (result) {
                    res.write(JSON.stringify(result));
                }
            } catch(error) {
                res.writeHead(500);
                res.write(JSON.stringify({
                    error: error.message,
                }));
                console.log(`API error for ${req.method} ${apiName}: ${error.message}`);
                console.log(error.stack);
            }
            res.end();
        } else if (req.url.endsWith(".js")) {
            const filePath = path.resolve(__dirname, req.url);
            if (!fs.existsSync(filePath)) {
                console.error("Couldn't find JS file", req.url);
                res.writeHead(404);
                res.end();
            } else {
                const content = fs.readFileSync(filePath);
                res.writeHead(200, {
                    'Content-Type': 'text/javascript',
                });
                res.write(content);
                res.end();
            }
        } else {
            console.error("Unexpected:", req.url)
            res.writeHead(404);
            res.end();
        }
    });
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});