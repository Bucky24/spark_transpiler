// This is a js based runner for spark, because Python is unbelievely stupid with how it deals with subprocesses

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");


const args = process.argv.slice(2);
if (args.length === 0) {
    console.log("Usage: spark <file>");
    process.exit(1);
}

const processedArgs = {};
let flag = null;
for (const arg of args) {
	if (arg.startsWith("--")) {
		if (flag) {
			processedArgs[flag] = true;
		}
		flag = arg.substring(2);
	} else if (arg.startsWith("-")) {
		if (flag) {
			processedArgs[flag] = true;
		}
		flag = arg.substring(1);
	} else {
		if (flag) {
			processedArgs[flag] = arg;
			flag = null;
		} else {
			processedArgs.files = [
				...processedArgs.files || [],
				arg,
			];
		}
	}
}

function compileFiles(files, pythonPath) {
	return new Promise((resolve, reject) => {
		let compileArgs = [];
		try {
			//let preserveCache = true;
			compileArgs = [
				path.resolve(__dirname, "./spark.py"),
				"--base_directory",
				path.resolve(processedArgs.base_directory),
				"--build_directory",
				path.resolve(processedArgs.build_directory),
				"--lang",
				processedArgs.lang,
			];
			//if (preserveCache) {
			//	compileArgs.push("--single_file");
			//}
			compileArgs = compileArgs.concat(files);
		} catch (error) {
			reject(error);
		}

		proc = spawn(pythonPath, compileArgs);
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
				if (line.includes("FAILURE")) {
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
let watchers = {};
let doingCompile = false;
let reloadFromWatcher = false;
let activeOutfile = false;

function closeWatchers() {
    if (watchers.length !== 0) {
        Object.values(watchers).forEach((watcher) => {
            watcher.close();
        });
        watchers = {};
    }
}

function createWatchers(files) {
	files.forEach((file) => {
		if (!watchers[file]) {
			watchers[file] = fs.watch(file, (eventType) => {
				if (eventType === "change" && !doingCompile) {
					console.log("Changes detected, recompiling");
					reloadFromWatcher = true;
					doCompile(file);
				}
			});
		}
	});
}

function doCompile(pythonPath) {
	if (activeProc) {
		activeProc.kill();
		activeProc = null;
	}
	doingCompile = true;
	return compileFiles(processedArgs.files, pythonPath).then(({ outFile, all_files }) => {
		doingCompile = false;
		return new Promise((resolve, reject) => {
			if (outFile) {
				activeOutfile = outFile;
			}
            try {
                createWatchers(all_files);
    		    console.log("Executing...");
    		    console.log("---------------------------------------------------------");
    			activeProc = executeFile(activeOutfile);
	
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

async function checkPython() {
	let pythonCommand = "python";

	let checkPython = new Promise((resolve, reject) => {
		proc = spawn(pythonCommand, ['--version']);
		proc.on('error', (err) => {
			if (err.message.startsWith("Error: spawn python ENOENT")) {
				resolve(false);
			}
		});

		proc.on('exit', (code) => {
			resolve(code == 0);
		});

		proc.on('close', (code) => {
			resolve(code == 0);
		});
	});
	let exists = await checkPython;

	if (!exists) {
		pythonCommand = "python3";

		checkPython = new Promise((resolve, reject) => {
			proc = spawn(pythonCommand, ['--version']);
			proc.on('error', (err) => {
				if (err.message.startsWith("Error: spawn python ENOENT")) {
					resolve(false);
				}
			});
	
			proc.on('exit', (code) => {
				resolve(code == 0);
			});
	
			proc.on('close', (code) => {
				resolve(code == 0);
			});
		});
		exists = await checkPython;
	}

	if (!exists) {
		console.log("Could not find python!");
		process.exit(1);
	}

	return pythonCommand;
}

checkPython().then((pythonPath) => {
	return doCompile(pythonPath)
}).catch((error) => {
	console.log(error);
});
