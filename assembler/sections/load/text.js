const { merge } = require('../../utils/common');
const { hexToBin, dec32, strToBin, empty, dec64 } = require('../../utils/binary');
const { LC_SEGMENT_64, PAGE_TEXT } = require('../../constants/assembler');
const { PAGE_TEXT_HEADER_SIZE, PAGE_TEXT_FILE_SIZE, PAGE_SUB_HEADER_SIZE } = require('../../constants/internal');
const load_sub = require("../load_sub");

function text(data) {
    let sections = [];
    sections = merge(sections, hexToBin(LC_SEGMENT_64));
    // size
    let headerSize = PAGE_TEXT_HEADER_SIZE + PAGE_SUB_HEADER_SIZE * data.children.length;
    let vmSize = 0;
    for (const subsection of data.children) {
        vmSize += subsection.size;
    }

    sections = merge(sections, dec32(headerSize));
    // name
    sections = merge(sections, strToBin(PAGE_TEXT, 16));
    // vm address
    sections = merge(sections, dec64(data.start));
    // vm size
    sections = merge(sections, dec64(vmSize));
    // file offset
    sections = merge(sections, empty(8));
    // file size
    sections = merge(sections, dec64(vmSize));
    
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
    sections = merge(sections, empty(4));

    let sub_sections = [];
    // so the start here is actual address
    let start = data.start;
    // the offset is the vm offset
    let offset = 0;
    for (const subsection of data.children) {
        start += subsection.size;
        sub_sections = merge(sub_sections, load_sub({
            ...subsection,
            start,
            offset,
        }));
        offset += subsection.size;
    }

    sections = merge(sections, sub_sections);

    return sections;
}

module.exports = text;