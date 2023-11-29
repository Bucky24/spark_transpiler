const { merge } = require('../../utils/common');
const { hexToBin, dec32, strToBin, empty, dec64 } = require('../../utils/binary');
const { LC_SEGMENT_64, PAGE_ZERO_NAME } = require('../../constants/assembler');

function pagezero(data) {
    let sections = [];
    sections = merge(sections, hexToBin(LC_SEGMENT_64));
    // size
    sections = merge(sections, dec32(72));
    // name
    sections = merge(sections, strToBin(PAGE_ZERO_NAME, 16));
    // vm address
    sections = merge(sections, empty(8));
    // vm size
    sections = merge(sections, dec64(data.size));
    // file offset
    sections = merge(sections, empty(8));
    // file size
    sections = merge(sections, empty(8));
    // max vm protection
    sections = merge(sections, empty(4));
    // init vm protection
    sections = merge(sections, empty(4));
    // section count
    sections = merge(sections, empty(4));
    // flags
    sections = merge(sections, empty(4));

    return sections;
}

module.exports = pagezero;