const fs = require("fs");
const path = require("path");

let mysql = null;

function getMysql() {
    if (!mysql) {
        mysql = require('mysql');
    }
    
    return mysql;
}

const dataCacheDir = path.resolve(__dirname, "..", "sparkDataCache");

class Table {
    constructor(tableName, fields, storageType = Table.SOURCE_FILE, version = 1) {
        Table.init();
        
        this.tableName = tableName;
        this.version = version;
        this.fields = fields;
        this.storageType = storageType;
        this.tableFile = path.join(dataCacheDir, `${tableName}.json`);
        if (!fs.existsSync(this.tableFile)) {
            this.data = [];
            this.writeData();
        } else {
            this.readData();
        }
    }
    
    setConfig(config) {
        this.config = config;
        this.conn = null;
    }
    
    _getConn() {
        return new Promise((resolve, reject) => {
            if (!this.conn) {
                if (this.storageType === Table.SOURCE_MYSQL) {
                    const mysql = getMysql();
                    const conn = mysql.createConnection(this.config);
                    conn.connect((err) => {
                        if (err) {
                            console.error("Unable to connect to database", err);
                            resolve(null);
                        } else {
                            this.conn = conn;
                            resolve(this.conn);
                        }
                    });
                } else {
                    console.error("Don't know how to get connection for " + this.storageType);
                    resolve(null);
                }
            } else {
                resolve(this.conn);
            }
        });
    }
    
    writeData() {
        const finalData = {
            "table": this.tableName,
            "data": this.data,
        };
        if (this.storageType === Table.SOURCE_FILE) {
            const dataString = JSON.stringify(finalData, null, 4);
            fs.writeFileSync(this.tableFile, dataString);
        }
    }
    
    readData() {
        if (this.storageType === Table.SOURCE_FILE) {
            const dataString = fs.readFileSync(this.tableFile);
            const dataJson = JSON.parse(dataString);
            this.data = dataJson.data;
        }
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
    
    _getTable() {
        return `${this.tableName}_v${this.version}`;
    }
    
    async load(params) {
        if (this.storageType === Table.SOURCE_FILE) {
            const matching = this.data.filter(this._filter(params));
        
            return matching;
        } else if (this.storageType === Table.SOURCE_MYSQL) {
            const conn = await this._getConn();
            let query = "SELECT * FROM " + this._getTable();
            const params = [];
            const paramStrings = Object.keys(params).map((key) => {
                const value = params[key];
                params.push(value);
                return `${key} = ?`;
            });
            if (paramStrings.length > 0) {
                const paramString = paramStrings.join(" AND ");
                query += " WHERE " + paramStrings;
            }
            query = mysql.format(query, params);
            const promise = new Promise((resolve, reject) => {
                conn.query(query, (error, results, fields) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(results);
                    }
                });
            });
            const results = await promise;
            return results;
        } else {
            console.error("Don't know how to write data for " + this.storageType);
        }
    }
    
    async update(search, update) {
        if (this.storageType === Table.SOURCE_FILE) {
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
        } else if (this.storageType === Table.SOURCE_MYSQL) {
            const conn = await this._getConn();
            let query = "UPDATE " + this._getTable() + " SET ";
            const params = [];
            const updateList = Object.keys(update).map((key) => {
                const value = update[key];
                params.push(value);
                return `${key} = ?`;
            });
            query += `${updateList.join(' ')} WHERE `;
            const searchList = Object.keys(search).map((key) => {
                const value = search[key];
                params.push(value);
                return `${key} = ?`;
            });
            query += searchList.join(' ');

            query = mysql.format(query, params);
            const promise = new Promise((resolve, reject) => {
                conn.query(query, (error, results, fields) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(results);
                    }
                });
            });
            await promise;
        } else {
            console.error("Don't know how to write data for " + this.storageType);
        }
    }
    
    async insert(data) {
        if (this.storageType === Table.SOURCE_FILE) {
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
        } else if (this.storageType === Table.SOURCE_MYSQL) {
            const conn = await this._getConn();
            let query = "INSERT INTO " + this._getTable() + " ";
            const params = [];
            const fieldList = Object.keys(data);
            const valueList = fieldList.map((field) => {
                const value = data[field];
                params.push(value);
                return '?';
            });
            query += `(${fieldList.join(',  ')}) VALUES(${valueList.join(', ')})`;
            query = mysql.format(query, params);
            const promise = new Promise((resolve, reject) => {
                conn.query(query, (error, results, fields) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(results);
                    }
                });
            });
            const result = await promise;
            return result;
        } else {
            console.error("Don't know how to insert data for " + this.storageType);
        }
    }
}

Table.STRING = "type/string";
Table.INT = "type/int";
Table.AUTO = "meta/auto";

Table.SOURCE_FILE = "source/file";
Table.SOURCE_MYSQL = "source/mysql";

Table.init = function() {
    if (!fs.existsSync(dataCacheDir)) {
        fs.mkdirSync(dataCacheDir);
    }
}

module.exports = {
    Table,
}