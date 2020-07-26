import argparse
import os
import struct
import sys

CHECKSUMADR = 0xFFDC

sums = {
    0x0349: {
        "name": "BS Sutte Hakkun Event Version",
        "huffroot": 0x122D0,
        "headeramount": 0x22D,
        "headerroot": 0x10000,
    },
    0x47C9: {
        "name": "BS Sutte Hakkun 2 6-3",
        "huffroot": 0x12390,
        "headeramount": 0x239,
        "headerroot": 0x10000,
    },
    0x654C: {
        "name": "BS Sutte Hakkun 2 10-8",
        "huffroot": 0x12390,
        "headeramount": 0x239,
        "headerroot": 0x10000,
    },
    0xFD66: {
        "name": "BS Sutte Hakkun 98 Winter Event Version",
        "huffroot": 0x12390,
        "headeramount": 0x239,
        "headerroot": 0x10000,
    },
    0xF450: {
        "name": "Sutte Hakkun (NP)",
        "huffroot": 0x30000,
        "headeramount": 0x3EA,
        "headerroot": 0x30BFE,
    }
}


def mdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def getB(number=1):
    return int.from_bytes(rom.read(number), byteorder='little')


def getTree(address):
    rom.seek(address)
    HUFFAMO, HUFFZERO = struct.unpack("HH", rom.read(4))
    huff_dict = []
    for _ in range(HUFFAMO):
        huff_dict.append(struct.unpack("xxHH", rom.read(6)))
    return HUFFZERO, huff_dict


def decompress(id, entry, hufftree):
    outputbuffer = bytearray()
    rom.seek(entry["pc_adr"])

    if entry["compressed_flag"]:
        zero, tree = hufftree

        pos = zero
        mask = []
        while len(outputbuffer) < entry["dec_size"]:
            if not mask:
                mb = getB()
                mask = [int(bit) for bit in format(mb, '08b')]
            while mask:
                step = mask.pop(0)
                pos = tree[pos][step]
                if tree[pos][0] == 0xFFFF:
                    outputbuffer.append(pos)
                    pos = zero
                    break

        print("${:04X} at ${:06X}\tDecompress done\t({:04X}/{:04X})".format(id, entry["pc_adr"], entry["comp_size"], entry["dec_size"]))
    else:
        outputbuffer = rom.read(entry["dec_size"])
        print("${:04X} at ${:06X}\tExtraction done\t({:04X}/{:04X})".format(id, entry["pc_adr"], entry["comp_size"], entry["dec_size"]))
    return outputbuffer


def getCheckSum(address):
    rom.seek(address)
    checksum = getB(2)
    if checksum in sums:
        adrs = sums[checksum]
        print("Checksum OK.\nYour version is: '{:s}'".format(adrs["name"]))
        return adrs
    else:
        print("Unknown checksum ({:04X})".format(checksum))


def snes2pc(addr):
    return addr - 0xC00000


def getHeaders(address, amount):
    rom.seek(address)
    headers = []
    for _ in range(amount):
        header = {
            "snes_adr": getB(4),
            "dec_size": getB(2),
            "comp_size": getB(2),
            "compressed_flag": getB(2),
            "pad": getB(6)
        }
        header["pc_adr"] = snes2pc(header["snes_adr"])
        headers.append(header)
    return headers


def main():
    global rom

    parser = argparse.ArgumentParser(description="A file decompressor/dumper for Sutte Hakkun (all versions)")
    parser.add_argument("rom_path", help="Path to ROM")
    parser.add_argument("-o", dest="output_dir", help="Output directory", default="out")
    args = parser.parse_args()

    with open(args.rom_path, "rb") as rom:
        # get checksum for correct version so the right addresses can be fetched
        lib = getCheckSum(CHECKSUMADR)
        if lib is None:
            print("Please verify that your ROM is a headerless known dump of Sutte Hakkun, any version will do.")
            sys.exit(1)

        odir = os.path.join(args.output_dir, lib["name"])
        mdir(odir)

        huff_adr, header_adr, header_amo = lib["huffroot"], lib["headerroot"], lib["headeramount"]

        tree = getTree(huff_adr)
        headers = getHeaders(header_adr, header_amo)

        for e, header in enumerate(headers):
            oname = os.path.join(odir, "{:04X}.smc".format(e))
            data = decompress(e, header, tree)
            with open(oname, "wb") as ofile:
                ofile.write(data)

        print("All done")


if __name__ == "__main__":
    main()
