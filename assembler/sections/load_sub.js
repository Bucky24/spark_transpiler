const { PAGE_TEXT } = require("../constants/assembler");
const { strToBin, dec64, dec32, empty, hexToBin } = require("../utils/binary");
const { merge } = require("../utils/common");

function load_sub(data) {
    let buffer = [];

    // section name
    buffer = merge(buffer, strToBin(data.name, 16));
    // segment name
    buffer = merge(buffer, strToBin(PAGE_TEXT, 16));
    // address
    buffer = merge(buffer, dec64(data.start));
    // size
    buffer = merge(buffer, dec64(data.size));
    // offset
    buffer = merge(buffer, dec32(data.offset));
    // alignment, no idea how to get this for now
    buffer = merge(buffer, empty(4));
    // relocations
    buffer = merge(buffer, empty(4));
    // relocations offset
    buffer = merge(buffer, empty(4));
    // flags
    buffer = merge(buffer, hexToBin(data.flags));
    // reserved 1
    buffer = merge(buffer, empty(4));
    // reserved 2
    buffer = merge(buffer, empty(4));
    // reserved 3
    buffer = merge(buffer, empty(4));

    return buffer;
}

module.exports = load_sub;