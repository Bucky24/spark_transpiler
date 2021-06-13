const fs = require("fs");
const path = require("path");

const dataCacheDir = path.resolve(__dirname, "..", "sparkDataCache");

class Table {
    constructor(tableName, fields) {
        Table.init();
        
        this.tableName = tableName;
        this.fields = fields;
        this.tableFile = path.join(dataCacheDir, `${tableName}.json`);
        if (!fs.existsSync(this.tableFile)) {
            this.data = [];
            this.writeData();
        } else {
            this.readData();
        }
    }
    
    writeData() {
        const finalData = {
            "table": this.tableName,
            "data": this.data,
        };
        const dataString = JSON.stringify(finalData, null, 4);
        fs.writeFileSync(this.tableFile, dataString);
    }
    
    readData() {
        const dataString = fs.readFileSync(this.tableFile);
        const dataJson = JSON.parse(dataString);
        this.data = dataJson.data;
    }
    
    _filter(params) {
        return (entity) => {
            for (const key of Object.keys(entity)) {
                if (params[key]) {
                    const value = entity[key];
                    
                    if (params[key] !== value) {
                        return false;
                    }
                }
            }
            return true;
        }
    }
    
    load(params) {
        const matching = this.data.filter(this._filter(params));
        
        return matching;
    }
    
    update(search, update) {
        const matching = [];
        
        const filter = this._filter(search);
        for (let i=0;i<this.data.length;i++) {
            const entry = this.data[i];
            if (filter(entry)) {
                matching.push(i);
            }
        }
        for (const match of matching) {
            const entry = this.data[match];
            Object.keys(update).forEach((key) => {
                const value = update[key];
                entry[key] = value;
            });
        } 
        
        this.writeData();
    }
    
    insert(data) {
        // generate any auto-increment fields that don't already exist
        this.fields.forEach((field) => {
            const meta = field.meta || [];
            const isAuto = meta.includes(Table.AUTO);
            if (data[field.name] || !isAuto) {
                return;
            }

            let highestValue = 0;
            this.data.forEach((item) => {
                if (item[field.name] > highestValue) {
                    highestValue = item[field.name];
                }
            });

            data[field.name] = highestValue + 1;
        });
        
        this.data.push(data);
        this.writeData();
    }
}

Table.STRING = "type/string";
Table.INT = "type/int";
Table.AUTO = "meta/auto";

Table.init = function() {
    if (!fs.existsSync(dataCacheDir)) {
        fs.mkdirSync(dataCacheDir);
    }
}

module.exports = {
    Table,
}