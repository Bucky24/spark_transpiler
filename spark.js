// This is a js based runner for spark, because Python is unbelievely stupid with how it deals with subprocesses

const { spawn } = require("child_process");
const path = require("path");

const args = process.argv.slice(2);

let proc = spawn("python", [path.resolve(__dirname, "./spark.py"), ...args]);

proc.stdout.on("data", (data) => {
    const str = data.toString();
    if (str.startsWith(">>>")) {
        const trimmed = str.trim();
        const file = trimmed.replace(">>>", "");

        console.log("Executing...");
        console.log("---------------------------------------------------------");
        executeFile(file).then(() => {
            console.log("---------------------------------------------------------");
        });
    } else {
        process.stdout.write(str);
    }
});

proc.stderr.on("data", (data) => {
	process.stderr.write(data.toString());
});

function executeFile(file) {
    return new Promise((resolve) => {
        const proc = spawn("node", [file]);

        proc.stdout.on("data", (data) => {
            const str = data.toString();
            process.stdout.write(str);
        });

        proc.stderr.on("data", (data) => {
            const str = data.toString();
            process.stderr.write(str);
        })

        proc.on('close', () => {
            resolve();
        });
    });
}