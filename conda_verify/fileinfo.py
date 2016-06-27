MAGIC = {
    '\xca\xfe\xba\xbe': 'MachO-universal',
    '\xce\xfa\xed\xfe': 'MachO-i386',
    '\xcf\xfa\xed\xfe': 'MachO-x86_64',
    '\xfe\xed\xfa\xce': 'MachO-ppc',
    '\xfe\xed\xfa\xcf': 'MachO-ppc64',
    'MZ\x90\x00': 'DLL',
    '\x7fELF': 'ELF',
}

DLL_Type = {
    0x0: 'UNKNOWN', 0x1d3: 'AM33', 0x8664: 'AMD64', 0x1c0: 'ARM',
    0xebc: 'EBC', 0x14c: 'I386', 0x200: 'IA64', 0x9041: 'M32R',
    0x266: 'MIPS16', 0x366: 'MIPSFPU', 0x466: 'MIPSFPU16', 0x1f0: 'POWERPC',
    0x1f1: 'POWERPCFP', 0x166: 'R4000', 0x1a2: 'SH3', 0x1a3: 'SH3DSP',
    0x1a6: 'SH4', 0x1a8: 'SH5', 0x1c2: 'THUMB', 0x169: 'WCEMIPSV2',
}


def get_object_type(data):
    head = data[:4]
    if head not in MAGIC:
        return None
    lookup = MAGIC.get(head)
    if lookup == 'DLL':
        pos = data.find('PE\0\0')
        if pos < 0:
            return "<no PE header found>"
        i = ord(data[pos + 4]) + 256 * ord(data[pos + 5])
        return "DLL " + DLL_Type.get(i)
    elif lookup.startswith('MachO'):
        return lookup
    elif lookup == 'ELF':
        return "ELF" + {'\x01': '32', '\x02': '64'}.get(data[4])
