const { merge } = require('../../utils/common');
const { hexToBin, dec32, strToBin, empty, dec64 } = require('../../utils/binary');
const { LC_SEGMENT_64, PAGE_TEXT } = require('../../constants/assembler');
const { PAGE_TEXT_HEADER_SIZE } = require('../../constants/internal');

function text(data) {
    let sections = [];
    sections = merge(sections, hexToBin(LC_SEGMENT_64));
    // size
    let size = PAGE_TEXT_HEADER_SIZE;
    sections = merge(sections, dec32(size));
    // name
    sections = merge(sections, strToBin(PAGE_TEXT, 16));
    // vm address
    sections = merge(sections, dec64(data.start));
    // vm size
    sections = merge(sections, dec64(data.size));
    // file offset
    sections = merge(sections, empty(8));
    // file size
    sections = merge(sections, dec64(data.size));
    
    let allProts = 0;
    for (const prot of data.protection) {
        allProts = allProts | prot;
    }

    // max vm protection
    sections = merge(sections, dec32(allProts));
    // init vm protection
    sections = merge(sections, dec32(allProts));
    // number of sections
    sections = merge(sections, dec32(data.children.length));
    // flags
    sections = merge(sections, empty(8));

    return sections;
}

module.exports = text;