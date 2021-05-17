const http = require("http");
const path = require("path");
const fs = require("fs");

const frontendFiles = {
//<FRONTEND_IMPORTS>
};

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

const server = http.createServer((req, res) => {
    // cut off the first slash
    req.url = req.url.substr(1);
    if (req.url === "") {
        serveFile(res, "stdlib_js_frontend_index.html");
    } else if (frontendFileKeys.includes(req.url)) {
        serveFile(res, frontendFiles[req.url]);
    } else {
        console.error("Unexpected:", req.url)
        res.writeHead(404);
        res.end();
    }
});

server.listen(port, hostname, () => {
    console.log(`Server running at http://${hostname}:${port}/`);
});