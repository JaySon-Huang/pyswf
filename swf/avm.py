#!/usr/bin/env python
#encoding=utf-8

from __future__ import print_function

from pprint import pprint

class ConstantPool(object):

    def __init__(self):
        super(ConstantPool, self).__init__()
        self.ints = [0,]
        self.uints = [0,]
        self.doubles = [0.0,]
        self.strings = ['*',]
        self.namespaces = ['*',]
        self.ns_sets = [None,]
        self.multinames = [None,]

    def parse(self, stream):
        pos = {}
        pos['beg'] = stream.tell()
        self._parse_numbers(stream)
        pos['end'] = stream.tell()
        print('parse numbers', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        string_count = stream.readEncodedU32()
        for i in range(string_count-1):
            size = stream.readEncodedU32()
            if size == 0:
                self.strings.append('')
                continue
            utf8_str = stream.read(size)
            self.strings.append(utf8_str)
        # print('strings({0}):'.format(len(self.strings)), end='');pprint(self.strings)
        pos['end'] = stream.tell()
        print('parse strings', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        namespace_count = stream.readEncodedU32()
        for i in range(namespace_count-1):
            kind = stream.readUI8()
            name = stream.readEncodedU32()
            self.namespaces.append((hex(kind), self.strings[name-1]))
        # print('namespace({0}):'.format(len(self.namespaces)), end='');pprint(self.namespaces)
        pos['end'] = stream.tell()
        print('parse namespaces', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        ns_set_count = stream.readEncodedU32()
        for i in range(ns_set_count-1):
            count = stream.readEncodedU32()
            ns = [stream.readEncodedU32() for i in range(count)]
            self.ns_sets.append(ns)
        # print('ns_set({0}):'.format(len(self.ns_sets)), end='');pprint(self.ns_sets)
        pos['end'] = stream.tell()
        print('parse ns_sets', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        self._parse_multiname(stream)
        # print('multinames({0}/{1}):'.format(len(self.multinames), multiname_count), end='');pprint(self.multinames)
        pos['end'] = stream.tell()
        print('parse multinames', pos['end'] - pos['beg'])

    def _parse_numbers(self, stream):
        int_count = stream.readEncodedU32()
        for i in range(int_count-1):
            self.ints.append(stream.readEncodedU32())
        # print('ints({0}/{1}): {2}'.format(
        #     len(self.ints), int_count, self.ints
        # ))

        uint_count = stream.readEncodedU32()
        for i in range(uint_count-1):
            self.uints.append(stream.readEncodedU32())
        # print('uints({0}/{1}): {2}'.format(
        #     len(self.uints), uint_count, self.uints
        # ))
        
        double_count = stream.readEncodedU32()
        for i in range(double_count-1):
            self.doubles.append(stream.readDOUBLE())
        # print('doubles({0}/{1}): {2}'.format(
        #     len(self.doubles), double_count, self.doubles
        # ))

    def _parse_multiname(self, stream):
        multiname_count = stream.readEncodedU32()
        for i in range(multiname_count-1):
            kind = stream.readUI8()
            data = {}
            if   kind in (0x07, 0x0D):# QName/QNameA
                data['ns'] = stream.readEncodedU32()
                data['name'] = stream.readEncodedU32()
            elif kind in (0x0F, 0x10):# RTQName/RTQNameA
                data['name'] = stream.readEncodedU32()
            elif kind in (0x11, 0x12):# RTQNameL/RTQNameLA
                pass
            elif kind in (0x09, 0x0E):# Multiname/MultinameA
                data['name'] = stream.readEncodedU32()
                data['ns_set'] = stream.readEncodedU32()
            elif kind in (0x1B, 0x1C):# MultinameL/MultinameLA
                data['ns_set'] = stream.readEncodedU32()
            elif kind == 0x1d:# TYPENAME
                # according to
                # https://github.com/jindrapetrik/jpexs-decompiler/ \
                #   blob/master/libsrc/ffdec_lib/src/ \
                #   com/jpexs/decompiler/flash/abc/types/Multiname.java
                data['qname_index'] = stream.readEncodedU32() # Multiname index!!!
                params_length = stream.readEncodedU32()
                # multiname indices!
                data['params'] = [
                    stream.readEncodedU32() 
                    for _ in range(params_length)
                ]
            else:
                raise Exception('Unknown kind: {0:02x}'.format(kind))
            self.multinames.append(
                (hex(kind), data)
            )


class StInstanceInfo(object):

    CONSTANT_ClassSealed = 0x01
    CONSTANT_ClassFinal = 0x02
    CONSTANT_ClassInterface = 0x04
    CONSTANT_ClassProtectedNs = 0x08

    def __init__(self, stream):
        self._name = stream.readEncodedU32()
        self._super_name = stream.readEncodedU32()
        self._flags = stream.readUI8()
        if self._flags & self.CONSTANT_ClassProtectedNs:
            self._protectedNs = stream.readEncodedU32()
        else:
            self._protectedNs = 0
        self._intrf_count = stream.readEncodedU32()
        self._interfaces = []
        for _ in range(self.intrf_count):
            self._interfaces.append(stream.readEncodedU32())
        self._iinit = stream.readEncodedU32()
        # Trait
        self._trait_count = stream.readEncodedU32()
        self._traits = []
        for _ in range(self._trait_count):
            self._traits.append(TraitFactory.create(stream))

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        super_name = const_pool.multinames[self.super_name]
        protectedNs = const_pool.namespaces[self.protectedNs]
        interfaces = [const_pool.multinames[i] for i in self.interfaces]
        return '''<InstanceInfo {name}>
name: {name}
super_name: {super_name}
flags: 0x{self.flags:02x}
protectedNs: {protectedNs}
interfaces: {interfaces}
iinit: {self.iinit}
traits: {self.traits}
'''.format(
    self=self,
    name=name,
    super_name=super_name,
    protectedNs=protectedNs,
    interfaces=interfaces,
)

    @property
    def name(self):
        return self._name
    
    @property
    def super_name(self):
        return self._super_name
    
    @property
    def flags(self):
        return self._flags
    
    @property
    def protectedNs(self):
        return self._protectedNs
    
    @property
    def intrf_count(self):
        return self._intrf_count
    
    @property
    def interfaces(self):
        return self._interfaces
    
    @property
    def iinit(self):
        return self._iinit
    
    @property
    def trait_count(self):
        return self._trait_count
    
    @property
    def traits(self):
        return self._traits

class StTraitBase(object):

    def __init__(self, name, kind):
        super(StTraitBase, self).__init__()
        self.name = name
        self.kind = kind
        self.metadatas = []


class StTraitSlot(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitSlot, self).__init__(name, kind)
        self.slot_id = 0
        self.type_name = 0
        self.vindex = 0
        self.vkind = 0

    def __repr__(self):
        return '<StTraitSlot {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitSlot {name}>
name: {name}
kind: 0x{self.kind:02x}
slot_id: {self.slot_id}
type_name: {self.type_name}
vindex: {self.vindex}
vkind: {self.vkind}
metadatas: {self.metadatas}
</StTraitSlot>
'''.format(
    name=name,
    self=self
)

class StTraitClass(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitClass, self).__init__(name, kind)
        self.slot_id = 0
        self.classi = 0

    def __repr__(self):
        return '<StTraitClass {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitClass {name}>
name: {name}
kind: 0x{self.kind:02x}
slot_id: {self.slot_id}
classi: {self.classi}
metadatas: {self.metadatas}
</StTraitClass>
'''.format(
    name=name,
    self=self
)


class StTraitFunction(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitFunction, self).__init__(name, kind)
        self.disp_id = 0
        self.function = 0

    def __repr__(self):
        return '<StTraitFunction {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitFunction {name}>
name: {name}
kind: 0x{self.kind:02x}
disp_id: {self.disp_id}
function: {self.function}
metadatas: {self.metadatas}
</StTraitFunction>
'''.format(
    name=name,
    self=self
)


class StTraitMethod(StTraitBase):

    def __init__(self, name, kind):
        super(StTraitMethod, self).__init__(name, kind)
        self.disp_id = 0
        self.method = 0

    def __repr__(self):
        return '<StTraitMethod {0}>'.format(self.name)

    def detail(self, const_pool):
        name = const_pool.multinames[self.name]
        return '''<StTraitMethod {name}>
name: {name}
kind: 0x{self.kind:02x}
disp_id: {self.disp_id}
method: {self.method}
metadatas: {self.metadatas}
</StTraitMethod>
'''.format(
    name=name,
    self=self
)


class TraitFactory(object):

    Trait_Slot = 0
    Trait_Method = 1
    Trait_Getter = 2
    Trait_Setter = 3
    Trait_Class = 4
    Trait_Function = 5
    Trait_Const = 6

    ATTR_Final = 1
    ATTR_Override = 2
    ATTR_Metadata = 4

    @classmethod
    def create(cls, stream):
        name = stream.readEncodedU32()
        kind = stream.readUI8()
        trait_type = kind & 0x0f
        if   trait_type in (cls.Trait_Slot, cls.Trait_Const):
            trait = StTraitSlot(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.type_name = stream.readEncodedU32()
            trait.vindex = stream.readEncodedU32()
            if trait.vindex != 0:
                trait.vkind = stream.readUI8()
        elif trait_type == cls.Trait_Class:
            trait = StTraitClass(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.classi = stream.readEncodedU32()
        elif trait_type == cls.Trait_Function:
            trait = StTraitFunction(name, kind)
            trait.slot_id = stream.readEncodedU32()
            trait.function = stream.readEncodedU32()
        elif trait_type in (cls.Trait_Method, cls.Trait_Getter, cls.Trait_Setter):
            trait = StTraitMethod(name, kind)
            trait.disp_id = stream.readEncodedU32()
            trait.method = stream.readEncodedU32()
        else:
            raise Exception('Unknown trait type: {0:02x}'.format(trait_type))
        # attr
        if (kind>>4) & cls.ATTR_Metadata:
            metadata_count = stream.readEncodedU32()
            for k in range(metadata_count):
                trait.metadatas.append(stream.readEncodedU32())
        return trait

class ABCFile(object):

    def __init__(self):
        super(ABCFile, self).__init__()
        self._version = {
            'minor': 0,
            'major': 0,
        }
        self._const_pool = ConstantPool()
        self._methods = []
        self._metadatas = []
        self._instances = []
        self._classes = []
        self._scripts = []
        self._method_bodies = []

    @property
    def version(self):
        return self._version

    @property
    def const_pool(self):
        return self._const_pool

    @property
    def methods(self):
        return self._methods
    
    @property
    def metadatas(self):
        return self._metadatas
    
    @property
    def instances(self):
        return self._instances
    
    @property
    def classes(self):
        return self._classes
    
    @property
    def scripts(self):
        return self._scripts

    @property
    def method_bodies(self):
        return self._method_bodies
    
    def parse(self, stream):
        self._version['minor'] = stream.readUI16()
        self._version['major'] = stream.readUI16()
        print('0x{0:04x}, 0x{1:04x}'.format(
            self._version['minor'], self._version['major']
        ))
        pos = {}
        
        self.const_pool.parse(stream)

        pos['beg'] = stream.tell()
        self._methods = self._parse_methods(stream)
        pos['end'] = stream.tell()
        # print('parse methods', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        self._metadatas = self._parse_metadas(stream)
        pos['end'] = stream.tell()
        # print('parse metadatas', pos['end'] - pos['beg'])
        # pprint(self.metadatas)

        # parse instance_info && class_info
        pos['beg'] = stream.tell()
        class_count = stream.readEncodedU32()
        self._instances = self._parse_instances(stream, class_count)
        pos['end'] = stream.tell()
        # print('parse instances', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        self._classes = self._parse_classes(stream, class_count)
        pos['end'] = stream.tell()
        # print('parse classes', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        self._scripts = self._parse_scripts(stream)
        pos['end'] = stream.tell()
        # print('parse scripts', pos['end'] - pos['beg'])

        pos['beg'] = stream.tell()
        self._method_bodies = self._parse_method_bodies(stream)
        pos['end'] = stream.tell()
        # print('parse method body', pos['end'] - pos['beg'])

        # from IPython import embed;embed();

    def _parse_methods(self, stream):
        methods = []
        method_count = stream.readEncodedU32()
        for i in range(method_count):
            param_count = stream.readEncodedU32()
            return_type = stream.readEncodedU32()
            param_types = []
            for j in range(param_count):
                param_types.append(stream.readEncodedU32())
            name = stream.readEncodedU32()
            flags = stream.readUI8()
            if flags & 0x01:# NEED_ARGUMENTS
                pass
            if flags & 0x02:# NEED_ACTIVATION
                pass
            if flags & 0x04:# NEED_REST
                pass
            if flags & 0x08:# HAS_OPTIONAL
                options = self._parse_method_options(stream)
            if flags & 0x40:# SET_EXNS
                pass
            if flags & 0x80:# HAS_PARAM_NAMES
                param_names = []
                for j in range(param_count):
                    param_names.append(stream.readEncodedU32())
        return methods

    def _parse_method_options(self, stream):
        option_count = stream.readEncodedU32()
        for i in range(option_count):
            val = stream.readEncodedU32()
            kind = stream.readUI8()

    def _parse_metadas(self, stream):
        metadatas = []
        metadata_count = stream.readEncodedU32()
        for _ in range(metadata_count):
            name = stream.readEncodedU32()
            name = self.const_pool.strings[name-1]
            item_count = stream.readEncodedU32()
            items = []
            for j in range(item_count):
                key = stream.readEncodedU32()
                value = stream.readEncodedU32()
                items.append({
                    'key': self.const_pool.strings[key-1],
                    'value': self.const_pool.strings[value-1],
                })
            metadatas.append({
                'name': name,
                'items': items,
            })
        return metadatas

    def _parse_instances(self, stream, class_count):
        instances = []
        for _ in range(class_count):
            instance = StInstanceInfo(stream)
            # print(instance.detail(self.const_pool))
            # for trait in instance.traits:
            #     print(trait.detail(self.const_pool))
            instances.append(instance)

    def _parse_classes(self, stream, class_count):
        classes = []
        for _ in range(class_count):
            cinit = stream.readEncodedU32()
            trait_count = stream.readEncodedU32()
            traits = []
            for j in range(trait_count):
                trait = TraitFactory.create(stream)
                traits.append(trait)
            classes.append({
                'cinit': cinit,
                'traits': traits,
            })
        return classes

    def _parse_scripts(self, stream):
        scripts = []
        script_count = stream.readEncodedU32()
        for _ in range(script_count):
            init = stream.readEncodedU32()
            trait_count = stream.readEncodedU32()
            traits = []
            for j in range(trait_count):
                trait = TraitFactory.create(stream)
                traits.append(trait)
            scripts.append({
                'init': init,
                'traits': traits,
            })
        return scripts

    def _parse_method_bodies(self, stream):
        bodies = []
        method_body_count = stream.readEncodedU32()
        for _ in range(method_body_count):
            method = stream.readEncodedU32()
            max_stack = stream.readEncodedU32()
            local_count = stream.readEncodedU32()
            init_scope_depth = stream.readEncodedU32()
            max_scope_depth = stream.readEncodedU32()
            code_length = stream.readEncodedU32()
            code = stream.read(code_length)
            exception_count = stream.readEncodedU32()
            for j in range(exception_count):
                from_ = stream.readEncodedU32()
                to = stream.readEncodedU32()
                target = stream.readEncodedU32()
                exc_type = stream.readEncodedU32()
                var_name = stream.readEncodedU32()
            trait_count = stream.readEncodedU32()
            for j in range(trait_count):
                trait = TraitFactory.create(stream)
