// This is a js based runner for spark, because Python is unbelievely stupid with how it deals with subprocesses

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");


const args = process.argv.slice(2);
if (args.length === 0) {
    console.log("Usage: spark <file>");
    process.exit(1);
}

function compileFiles() {
	return new Promise((resolve, reject) => {
		let proc = spawn("python", [path.resolve(__dirname, "./spark.py"), ...args]);

		proc.stdout.on("data", (data) => {
		    const str = data.toString();
		    if (str.startsWith(">>>")) {
		        const trimmed = str.trim();
		        const jsonOutput = trimmed.replace(">>>", "");
                const json = JSON.parse(jsonOutput);

				resolve(json);
		    } else {
		        process.stdout.write(str);
		    }
		});

		proc.stderr.on("data", (data) => {
			const error = data.toString();
			process.stderr.write(error);
			const lines = error.split("\n");
			let compileFailed = false;
			lines.forEach((line) => {
				if (line === "FAILURE") {
					compileFailed = true;
				}
			});

			if (compileFailed) {
				reject();
			}
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
let watchers = [];
let doingCompile = false;
let reloadFromWatcher = false;

function closeWatchers() {
    if (watchers.length !== 0) {
        watchers.forEach((watcher) => {
            watcher.close();
        });
        watchers = [];
    }
}

function createWatchers(files) {
    closeWatchers();
    
    watchers = files.map((file) => {
        return fs.watch(file, (eventType, file) => {
        	if (eventType === "change" && !doingCompile) {
        		console.log("Changes detected, recompiling");
        		reloadFromWatcher = true;
        		doCompile();
        	}
        });
    });
}

function doCompile() {
	if (activeProc) {
		activeProc.kill();
		activeProc = null;
	}
	doingCompile = true;
	return compileFiles().then(({ outFile, all_files }) => {
		doingCompile = false;
		return new Promise((resolve, reject) => {
            try {
                createWatchers(all_files);
    		    console.log("Executing...");
    		    console.log("---------------------------------------------------------");
    			activeProc = executeFile(outFile);
	
    		    activeProc.on('close', () => {
    				if (!reloadFromWatcher) {
    		    		console.log("---------------------------------------------------------");
    					closeWatchers();
    				}
    				reloadFromWatcher = false;
    		        resolve();
    		    });
            } catch (error) {
                reject(error);
            }
		});
	}).catch(() => {
		doingCompile = false;
	});
}

doCompile().catch((error) => {
    console.log(error);
});