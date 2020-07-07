import struct
import os, sys

CHECKSUMADR = 0xFFDC

outputpath = "./out/"
rompath = "/Users/whatever/ROMS/BS Sutte Hakkun (J).smc"

sums = {
    0x0349 : {
        "name" : "BS Sutte Hakkun Event Version",
        "huffroot": 0x122D0,
        "headeramount" : 0x22D,
        "headerroot" : 0x10000,
    },
    0x47C9 : {
        "name" : "BS Sutte Hakkun 2 6-3",
        "huffroot" : 0x12390,
        "headeramount" : 0x239,
        "headerroot" : 0x10000,
    },
    0x654C : {
        "name" : "BS Sutte Hakkun 2 10-8",
        "huffroot" : 0x12390,
        "headeramount" : 0x239,
        "headerroot" : 0x10000,
    },
    0xFD66 : {
        "name" : "BS Sutte Hakkun 98 Winter Event Version",
        "huffroot" : 0x12390,
        "headeramount" : 0x239,
        "headerroot" : 0x10000,
    },
    0xF450 : {
        "name" : "Sutte Hakkun (NP)",
        "huffroot": 0x30000,
        "headeramount" : 0x3EA,
        "headerroot" : 0x30BFE,
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
    for i in range(0, HUFFAMO):
        huff_dict.append(struct.unpack("xxHH", rom.read(6)))
    return [HUFFZERO, huff_dict]

def decompress(entry, hufftree):
    outputbuffer = bytearray()
    rom.seek(entry["pc_adr"])
    
    if entry["compressed_flag"]:
        zero = hufftree[0]
        tree = hufftree[1]
        
        done = False
        while True:
            mb = getB()
            mask = [int(bit) for bit in list(bin(mb)[2:].zfill(8))]
            
            while len(mask) > 0:
                step = mask.pop(0)
                dest = tree[zero][step]
                if tree[dest][0] == 0xFFFF:
                    outbyte = dest
                    outputbuffer.append(outbyte)
                    zero = hufftree[0]
                    if len(outputbuffer) == entry["dec_size"]:
                        done = True
                        break
                else:
                    zero = dest
            if done:
                break
        print("${:04X} at ${:06X}\tDecompress done\t({:04X}/{:04X})".format(e,entry["pc_adr"], entry["comp_size"], entry["dec_size"]))
    else:
        outputbuffer = rom.read(entry["dec_size"])
        print("${:04X} at ${:06X}\tExtraction done\t({:04X}/{:04X})".format(e,entry["pc_adr"], entry["comp_size"], entry["dec_size"]))
    return outputbuffer

def getCheckSum(adress):
    rom.seek(adress)
    checksum = getB(2)
    try:
        adrs = sums[checksum]
        print("Checksum OK.\nYour version is: '{:s}'".format(adrs["name"]))
        return adrs
    except KeyError:
        print("Unknown checksum ({:04X}).\nPlease verify that your ROM is a headerless known dump of Sutte Hakkun, any version will do.".format(checksum))
        return

def snes2pc(addr):
    return addr - 0xC00000

def getHeaders(adress, amount):
    rom.seek(adress)
    headers = {}
    for h in range(0, amount):
        headers[h] = {
            "snes_adr" : getB(4),
            "dec_size" : getB(2),
            "comp_size" : getB(2),
            "compressed_flag" : getB(2),
            "pad" : getB(6)
            }
        headers[h]["pc_adr"] = snes2pc(headers[h]["snes_adr"])
    
    return headers

#the main code
with open(rompath, "rb") as rom:
    #get checksum for correct version so the right addresses can be fetched
    lib = getCheckSum(CHECKSUMADR)
    
    oname = outputpath+lib["name"]+"/"
    mdir(oname)
    
    huff_adr, header_adr, header_amo = lib["huffroot"], lib["headerroot"], lib["headeramount"]
    
    tree = getTree(huff_adr)
    headers = getHeaders(header_adr, header_amo)
    
    for e in headers:
        data = decompress(headers[e], tree)
        ofile = open(oname+"{:04X}.smc".format(e), "wb")
        ofile.write(data)
        ofile.close()
    print("All done")