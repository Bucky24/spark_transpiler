// This is a js based runner for spark, because Python is unbelievely stupid with how it deals with subprocesses

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const args = process.argv.slice(2);

function compileFiles(files) {
	return new Promise((resolve, reject) => {
		let proc = spawn("python", [path.resolve(__dirname, "./spark.py"), ...args]);

		proc.stdout.on("data", (data) => {
		    const str = data.toString();
		    if (str.startsWith(">>>")) {
		        const trimmed = str.trim();
		        const file = trimmed.replace(">>>", "");

				resolve(file);
		    } else {
		        process.stdout.write(str);
		    }
		});

		proc.stderr.on("data", (data) => {
			process.stderr.write(data.toString());
		});
	});
}

function executeFile(file) {
    const proc = spawn("node", [file]);

    proc.stdout.on("data", (data) => {
        const str = data.toString();
        process.stdout.write(str);
    });

    proc.stderr.on("data", (data) => {
        const str = data.toString();
        process.stderr.write(str);
    });
	
	return proc;
}

let activeProc = null;
let watcher = null;
let doingCompile = false;
let reloadFromWatcher = false;
function doCompile() {
	if (activeProc) {
		activeProc.kill();
		activeProc = null;
	}
	doingCompile = true;
	compileFiles(args).then((outputFile) => {
		doingCompile = false;
		return new Promise((resolve) => {
		    console.log("Executing...");
		    console.log("---------------------------------------------------------");
			activeProc = executeFile(outputFile);
	
		    activeProc.on('close', () => {
				if (!reloadFromWatcher) {
		    		console.log("---------------------------------------------------------");
					watcher.close();
				}
				reloadFromWatcher = false;
		        resolve();
		    });
		});
	});
}

doCompile();

watcher = fs.watch(args[0], (eventType, file) => {
	if (eventType === "change" && !doingCompile) {
		console.log("Changes detected, recompiling");
		reloadFromWatcher = true;
		doCompile();
	}
});