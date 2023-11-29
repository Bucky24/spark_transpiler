const fs = require("fs");
const path = require("path");

const { VM_PROD_READ, VM_PROD_EXECUTE, S_FLAGS } = require('./constants/assembler');
const { merge } = require("./utils/common");
const { header, load } = require('./sections');
const { LOAD_PAGE_ZERO, LOAD_TEXT, PAGE_ZERO_SIZE } = require("./constants/internal");

const outfile = "test";

const outPath = path.join(__dirname, outfile);

const sectionData = [
    { type: LOAD_PAGE_ZERO, size: PAGE_ZERO_SIZE },
    {
        type: LOAD_TEXT,
        start: PAGE_ZERO_SIZE,
        size: 0,
        protection: [VM_PROD_READ, VM_PROD_EXECUTE],
        children: [
            {
                name: '__text',
                size: 22,
                flags: S_FLAGS,
            },
        ],
    },
];

let bytes = [];

let sections = [];
for (const data of sectionData) {
    sections = merge(sections, load(data));
}

const sectionCount = sectionData.length;
const sectionSize = sections.length;
bytes = merge(bytes, header(sectionCount, sectionSize));
bytes = merge(bytes, sections);

const buffer = Buffer.from(bytes);

console.log(bytes, buffer);

fs.writeFileSync(outPath, buffer, "binary");