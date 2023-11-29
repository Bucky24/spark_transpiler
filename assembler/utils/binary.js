function hexToBin(hex) {
    if (hex.length % 2 !== 0) {
        throw new Error("Got string that was " + hex.length + " in length");
    }

    // split into character pairs
    const pairs = [];
    for (let i=0;i<hex.length;i+=2) {
        const ch = hex.substr(i, 2);
        pairs.push(ch);
    }

    // little endian
    pairs.reverse();

    return pairs.map(num => parseInt(num, 16));
}

function dec32(num) {
    const hex = num.toString(16);
    const hexExtended = hex.padStart(8, "0");
    return hexToBin(hexExtended);
}

function dec64(num) {
    const hex = num.toString(16);
    const hexExtended = hex.padStart(16, "0");
    return hexToBin(hexExtended);
}

function strToBin(string, length) {
    const padded = string.padEnd(length, "\0");

    // no reverse on this one
    return padded.split("").map(char => char.charCodeAt(0));
}

function empty(count) {
    const arr = [];
    for (let i=0;i<count;i++) {
        arr.push(0);
    }

    return arr;
}

module.exports = {
    hexToBin,
    dec32,
    dec64,
    strToBin,
    empty,
};