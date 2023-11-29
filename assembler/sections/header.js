const { hexToBin, dec32 } = require("../utils/binary");
const {
    MAGIC_NUMBER_HEX,
    CPU_TYPE_X86,
    CPU_SUBTYPE_X86_ALL,
    FILE_TYPE_EXECUTE,
} = require('../constants/assembler');
const { merge } = require("../utils/common");

function header(sectionCount, sectionSize) {
    let bytes = [];

    bytes = merge(bytes, hexToBin(MAGIC_NUMBER_HEX));
    bytes = merge(bytes, hexToBin(CPU_TYPE_X86));
    bytes = merge(bytes, hexToBin(CPU_SUBTYPE_X86_ALL));
    bytes = merge(bytes, hexToBin(FILE_TYPE_EXECUTE));
    // num of load commands
    bytes = merge(bytes, dec32(sectionCount));
    // size of load commands
    bytes = merge(bytes, dec32(sectionSize));
    // flags
    bytes = merge(bytes, [0,0,0,0]);
    // reserved
    bytes = merge(bytes, [0,0,0,0]);

    return bytes;
}

module.exports = header;