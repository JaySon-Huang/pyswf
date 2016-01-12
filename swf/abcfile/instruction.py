#!/usr/bin/env python
# encoding=utf-8

from __future__ import print_function

import struct
from six import BytesIO
from ..stream import SWFStream


def print_codes_name(code_bytes):
    stream = SWFStream(BytesIO(code_bytes))
    while 1:
        try:
            ch = stream.readUI8()
        except struct.error:
            break

        if ch == 0xa0:
            print("add")
        elif ch == 0xc5:
            print("add_i")
        elif ch == 0xa1:
            print("subtract")
        elif ch == 0xc6:
            print("subtract_i")
        elif ch == 0xa2:
            print("multiply")
        elif ch == 0xc7:
            print("multiply_i")
        elif ch == 0xa3:
            print("divide")
        elif ch == 0xa4:
            print("modulo")
        elif ch == 0x90:
            print("negate")
        elif ch == 0xc4:
            print("negate_i")

        elif ch == 0x86:
            index = stream.readEncodedU32()
            print("astype", index)
        elif ch == 0x87:
            print("astypelate")

        elif ch == 0xa8:
            print("bitand")
        elif ch == 0x97:
            print("bitnot")
        elif ch == 0xa9:
            print("bitor")
        elif ch == 0xaa:
            print("bitxor")

        elif ch == 0x41:
            arg_count = stream.readEncodedU32()
            print("call", arg_count)
        elif ch == 0x43:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callmethod", index, arg_count)
        elif ch == 0x46:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callproperty", index, arg_count)
        elif ch == 0x4c:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callproplex", index, arg_count)
        elif ch == 0x4f:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callpropvoid", index, arg_count)
        elif ch == 0x44:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callstatic", index, arg_count)
        elif ch == 0x45:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callsuper", index, arg_count)
        elif ch == 0x4e:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("callsupervoid", index, arg_count)
        elif ch == 0x78:
            print("checkfilter")

        elif ch == 0x80:
            index = stream.readEncodedU32()
            print("coerce", index)
        elif ch == 0x82:
            print("coerce_a")
        elif ch == 0x85:
            print("coerce_s")
        elif ch == 0x89:
            print("coerce_o")

        elif ch == 0x42:
            arg_count = stream.readEncodedU32()
            print("construct", arg_count)
        elif ch == 0x4a:
            index = stream.readEncodedU32()
            arg_count = stream.readEncodedU32()
            print("constructprop", index, arg_count)
        elif ch == 0x49:
            arg_count = stream.readEncodedU32()
            print("constructsuper", arg_count)

        elif ch == 0x70:
            print("convert_s")
        elif ch == 0x73:
            print("convert_i")
        elif ch == 0x74:
            print("convert_u")
        elif ch == 0x75:
            print("convert_d")
        elif ch == 0x76:
            print("convert_b")
        elif ch == 0x77:
            print("convert_o")

        elif ch == 0xef:
            debug_type = stream.readUI8()
            index = stream.readEncodedU32()
            reg = stream.readUI8()
            extra = stream.readEncodedU32()  # currently unused
            print("debug", debug_type, index, reg, extra)
        elif ch == 0xf0:
            linenum = stream.readEncodedU32()
            print("debugline", linenum)
        elif ch == 0xf1:
            index = stream.readEncodedU32()
            print("debugfile", index)

        elif ch == 0x94:
            index = stream.readEncodedU32()
            print("declocal", index)
        elif ch == 0xc3:
            index = stream.readEncodedU32()
            print("declocal_i", index)

        elif ch == 0x93:
            print("decrement")
        elif ch == 0xc1:
            print("decrement_i")

        elif ch == 0x6a:
            index = stream.readEncodedU32()
            print("deleteproperty", index)
        elif ch == 0x2a:
            print("dup")

        elif ch == 0x06:
            index = stream.readEncodedU32()
            print("dxns", index)
        elif ch == 0x07:
            print("dxnslate")

        elif ch == 0xab:
            print("equals")
        elif ch == 0xac:
            print("strictequals")
        elif ch == 0xad:
            print("lessthan")
        elif ch == 0xae:
            print("lessequals")
        elif ch == 0xaf:
            print("greaterthan")
        elif ch == 0xb0:
            print("greaterequals")

        elif ch == 0x71:
            print("esc_xelem")
        elif ch == 0x72:
            print("esc_xattr")

        elif ch == 0x5e:
            index = stream.readEncodedU32()
            print("findproperty", index)
        elif ch == 0x5d:
            index = stream.readEncodedU32()
            print("findpropstrict", index)

        elif ch == 0x59:
            index = stream.readEncodedU32()
            print("getdescendants", index)
        elif ch == 0x60:
            index = stream.readEncodedU32()
            print("getlex", index)
        elif ch == 0x64:
            print("getglobalscope")
        elif ch == 0x6e:
            slot_index = stream.readEncodedU32()
            print("getglobalslot", slot_index)
        elif ch == 0x6f:
            slot_index = stream.readEncodedU32()
            print("setglobalslot", slot_index)

        elif ch == 0x62:
            index = stream.readEncodedU32()
            print("getlocal", index)
        elif ch == 0x63:
            index = stream.readEncodedU32()
            print("setlocal", index)
        elif ch == 0xd0:
            print("getlocal0")
        elif ch == 0xd1:
            print("getlocal1")
        elif ch == 0xd2:
            print("getlocal2")
        elif ch == 0xd3:
            print("getlocal3")
        elif ch == 0xd4:
            print("setlocal0")
        elif ch == 0xd5:
            print("setlocal1")
        elif ch == 0xd6:
            print("setlocal2")
        elif ch == 0xd7:
            print("setlocal3")

        elif ch == 0x65:
            index = stream.readEncodedU32()
            print("getscopeobject", index)

        elif ch == 0x66:
            index = stream.readEncodedU32()
            print("getproperty", index)
        elif ch == 0x61:
            index = stream.readEncodedU32()
            print("setproperty", index)

        elif ch == 0x6c:
            slot_index = stream.readEncodedU32()
            print("getslot", slot_index)
        elif ch == 0x6d:
            slot_index = stream.readEncodedU32()
            print("setslot", slot_index)

        elif ch == 0x04:
            index = stream.readEncodedU32()
            print("getsuper", index)
        elif ch == 0x05:
            index = stream.readEncodedU32()
            print("setsuper", index)

        elif ch == 0x67:
            print("getouterscope")

        elif ch == 0x1f:
            print("hasnext")

        elif ch == 0x32:
            raise NotImplementedError('type of object_reg, index_reg remain unknown.')
            object_reg = None
            index_reg = None
            print("hasnext2", object_reg, index_reg)

        elif ch == 0x10:
            print("jump")
        elif ch == 0x0c:
            offset = stream.readS24()
            print("ifnlt", offset)
        elif ch == 0x0d:
            offset = stream.readS24()
            print("ifnle", offset)
        elif ch == 0x0e:
            offset = stream.readS24()
            print("ifngt", offset)
        elif ch == 0x0f:
            offset = stream.readS24()
            print("ifnge", offset)
        elif ch == 0x11:
            offset = stream.readS24()
            print("iftrue", offset)
        elif ch == 0x12:
            offset = stream.readS24()
            print("iffalse", offset)
        elif ch == 0x13:
            offset = stream.readS24()
            print("ifeq", offset)
        elif ch == 0x14:
            offset = stream.readS24()
            print("ifne", offset)
        elif ch == 0x15:
            offset = stream.readS24()
            print("iflt", offset)
        elif ch == 0x16:
            offset = stream.readS24()
            print("ifle", offset)
        elif ch == 0x17:
            offset = stream.readS24()
            print("ifgt", offset)
        elif ch == 0x18:
            offset = stream.readS24()
            print("ifge", offset)
        elif ch == 0x19:
            offset = stream.readS24()
            print("ifstricteq", offset)
        elif ch == 0x1a:
            offset = stream.readS24()
            print("ifstrictne", offset)

        elif ch == 0xb4:
            print("in")
        elif ch == 0x92:
            index = stream.readEncodedU32()
            print("inclocal", index)
        elif ch == 0xc2:
            index = stream.readEncodedU32()
            print("inclocal_i", index)

        elif ch == 0x91:
            print("increment")
        elif ch == 0xc0:
            print("increment_i")

        elif ch == 0x68:
            index = stream.readEncodedU32()
            print("initproperty", index)

        elif ch == 0xb1:
            print("instanceof")

        elif ch == 0xb2:
            index = stream.readEncodedU32()
            print("istype", index)
        elif ch == 0xb3:
            print("istypelate")

        elif ch == 0x08:
            index = stream.readEncodedU32()
            print("kill", index)
        elif ch == 0x09:
            print("label")
        elif ch == 0x1b:
            # FIXME
            default_offset = stream.readS24()
            case_count = stream.readEncodedU32()
            case_offsets = []
            for _ in range(case_count):
                case_offsets.append(stream.readS24())
            print("lookupswitch", default_offset, case_count, case_offsets)

        elif ch == 0xa5:
            print("lshift")
        elif ch == 0xa6:
            print("rshift")
        elif ch == 0xa7:
            print("urshift")

        elif ch == 0x57:
            print("newactivation")
        elif ch == 0x56:
            arg_count = stream.readEncodedU32()
            print("newarray", arg_count)
        elif ch == 0x5a:
            index = stream.readEncodedU32()
            print("newcatch", index)
        elif ch == 0x40:
            index = stream.readEncodedU32()
            print("newfunction", index)
        elif ch == 0x55:
            arg_count = stream.readEncodedU32()
            print("newobject", arg_count)
        elif ch == 0x58:
            index = stream.readEncodedU32()
            print("newclass", index)

        elif ch == 0x1e:
            print("nextname")
        elif ch == 0x23:
            print("nextvalue")
        elif ch == 0x02:
            print("nop")
        elif ch == 0x96:
            print("not")

        elif ch == 0x29:
            print("pop")
        elif ch == 0x1d:
            print("popscope")

        elif ch == 0x24:
            byte_value = stream.readUI8()
            print("pushbyte", byte_value)
        elif ch == 0x25:
            index = stream.readEncodedU32()
            print("pushshort", index)
        elif ch == 0x2c:
            index = stream.readEncodedU32()
            print("pushstring", index)
        elif ch == 0x2d:
            index = stream.readEncodedU32()
            print("pushint", index)
        elif ch == 0x2e:
            index = stream.readEncodedU32()
            print("pushuint", index)
        elif ch == 0x2f:
            index = stream.readEncodedU32()
            print("pushdouble", index)
        elif ch == 0x31:
            index = stream.readEncodedU32()
            print("pushnamespace", index)
        elif ch == 0x1c:
            print("pushwith")
        elif ch == 0x20:
            print("pushnull")
        elif ch == 0x21:
            print("pushundefined")
        elif ch == 0x26:
            print("pushtrue")
        elif ch == 0x27:
            print("pushfalse")
        elif ch == 0x28:
            print("pushnan")
        elif ch == 0x30:
            print("pushscope")

        elif ch == 0x2b:
            print("swap")

        elif ch == 0x03:
            print("throw")
        elif ch == 0x95:
            print("typeof")

        elif ch == 0x47:
            print("returnvoid")
        elif ch == 0x48:
            print("returnvalue")

        else:
            print("0x{0:02x}".format(ch))
