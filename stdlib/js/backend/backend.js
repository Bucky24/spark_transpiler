const fs = require("fs");
const path = require("path");

const dataCacheDir = path.resolve(__dirname, "..", "dataCache");

class Table {
   constructor(tableName, fields) {
       Table.init();

       this.tableName = tableName;
       this.tableFile = path.join(dataCacheDir, `${tableName}.json`);
       if (!fs.existsSync(this.tableFile)) {
           this.data = {};
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
}

Table.STRING = "type/string";
Table.init = function() {
    if (!fs.existsSync(dataCacheDir)) {
        fs.mkdirSync(dataCacheDir);
    }
}

module.exports = {
    Table,
}