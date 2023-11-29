const {
    LOAD_PAGE_ZERO,
    LOAD_TEXT,
} = require('../../constants/internal');
const pagezero = require('./pagezero');
const text = require('./text');

function load(data = {}) {
    switch (data.type) {
        case LOAD_PAGE_ZERO:
            return pagezero(data);
        case LOAD_TEXT:
            return text(data);
        default:
            throw new Error("Unknown load section type " + data.type);
    }
}

module.exports = load;