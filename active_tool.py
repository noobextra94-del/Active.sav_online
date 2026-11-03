import struct

def le_int(val): return struct.pack("<i", int(val))
def le_float(val): return struct.pack("<f", float(val))
def le_double(val): return struct.pack("<d", float(val))
def hexify(b): return " ".join(f"{x:02X}" for x in b)

def name_block(name):
    raw = name.encode("ascii") + b"\x00"
    size = le_int(len(raw))
    return hexify(size), hexify(raw)

def make_property_bytes(prop_type, name, val_data):
    n_size, n_hex = name_block(name)
    
    if prop_type == "FloatProperty":
        p_size, p_hex = name_block("FloatProperty")
        val_hex = hexify(le_float(float(val_data)))
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 04 00 00 00 00 00 00 00 00 {val_hex}")
        
    elif prop_type == "IntProperty":
        p_size, p_hex = name_block("IntProperty")
        val_hex = hexify(le_int(int(val_data)))
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 04 00 00 00 00 00 00 00 00 {val_hex}")
        
    elif prop_type == "BoolProperty":
        p_size, p_hex = name_block("BoolProperty")
        val_byte = "01" if str(val_data).lower() in ['true', '1', 'yes'] else "00"
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 00 00 00 00 00 00 00 00 {val_byte} 00")
        
    elif prop_type == "StringProperty":
        p_size, p_hex = name_block("StrProperty")
        str_bytes = str(val_data).encode("utf-8") + b"\x00"
        str_len = len(str_bytes)
        payload_size = le_int(4 + str_len)
        str_hex = hexify(le_int(str_len)) + " " + hexify(str_bytes)
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} {hexify(payload_size)} 00 00 00 00 00 {str_hex}")
        
    elif prop_type == "DoubleProperty":
        p_size, p_hex = name_block("DoubleProperty")
        val_hex = hexify(le_double(float(val_data)))
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 08 00 00 00 00 00 00 00 00 {val_hex}")
        
    elif prop_type == "VectorProperty":
        p_size, p_hex = name_block("StructProperty")
        struct_type_size, struct_type_hex = name_block("Vector")
        x, y, z = map(float, val_data.split(','))
        vector_hex = f"{hexify(le_float(x))} {hexify(le_float(y))} {hexify(le_float(z))}"
        return bytes.fromhex(f"{n_size} {n_hex} {p_size} {p_hex} 0C 00 00 00 00 00 00 00 {struct_type_hex} 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 {vector_hex}")
        
    return None

def inject_to_file(filepath, new_bytes):
    with open(filepath, "rb") as f:
        content = f.read()
    
    eof_marker = b"\x05\x00\x00\x00None\x00\x00"
    std_marker = b"\x05\x00\x00\x00None\x00"
    
    pos = content.rfind(eof_marker)
    if pos != -1:
        base = content[:pos]
    else:
        pos2 = content.rfind(std_marker)
        base = content[:pos2] if pos2 != -1 else content

    updated = base + new_bytes + eof_marker
    with open(filepath, "wb") as f:
        f.write(updated)
