#!/usr/bin/env python
# encoding=utf-8

from constant_pool import ConstantPool, StMultiname
from trait import TraitFactory


class StMethodInfo(object):

    NEED_ARGUMENTS  = 0x01
    NEED_ACTIVATION = 0x02
    NEED_REST       = 0x04
    HAS_OPTIONAL    = 0x08
    SET_EXNS        = 0x40
    HAS_PARAM_NAMES = 0x80

    def __init__(self, stream):
        param_count = stream.readEncodedU32()
        self.return_type = stream.readEncodedU32()
        self.param_types = []
        for j in range(param_count):
            self.param_types.append(stream.readEncodedU32())
        self.name = stream.readEncodedU32()
        self.flags = stream.readUI8()
        self.options = []
        self.param_names = []
        if self.flags & self.NEED_ARGUMENTS:
            pass
        if self.flags & self.NEED_ACTIVATION:
            pass
        if self.flags & self.NEED_REST:
            pass
        if self.flags & self.HAS_OPTIONAL:
            self.options = self._parse_options(stream)
        if self.flags & self.SET_EXNS:
            pass
        if self.flags & self.HAS_PARAM_NAMES:
            for j in range(param_count):
                self.param_names.append(stream.readEncodedU32())

    def _parse_options(self, stream):
        options = []
        option_count = stream.readEncodedU32()
        for _ in range(option_count):
            val = stream.readEncodedU32()
            kind = stream.readUI8()
            options.append({'val': val, 'kind': kind})
        return options

    def __repr__(self):
        return '<StMethodInfo {self.name}>'.format(self=self)


class StInstanceInfo(object):

    CONSTANT_ClassSealed      = 0x01
    CONSTANT_ClassFinal       = 0x02
    CONSTANT_ClassInterface   = 0x04
    CONSTANT_ClassProtectedNs = 0x08

    def __init__(self, stream):
        self.name = stream.readEncodedU32()
        self.super_name = stream.readEncodedU32()
        self.flags = stream.readUI8()
        if self.flags & self.CONSTANT_ClassProtectedNs:
            self.protectedNs = stream.readEncodedU32()
        else:
            self.protectedNs = 0
        self.intrf_count = stream.readEncodedU32()
        self.interfaces = []
        for _ in range(self.intrf_count):
            self.interfaces.append(stream.readEncodedU32())
        self.iinit = stream.readEncodedU32()
        # Trait
        self.trait_count = stream.readEncodedU32()
        self.traits = []
        for _ in range(self.trait_count):
            self.traits.append(TraitFactory.create(stream))

    def __repr__(self):
        return '<StInstanceInfo {}({})>'.format(self.name, self.super_name)

    def details(self, const_pool):
        interfaces = [const_pool.multinames[i] for i in self.interfaces]
        return '''<InstanceInfo {name}>
name: {self.name}
super_name: {self.super_name}
flags: 0x{self.flags:02x}
protectedNs: {self.protectedNs}
interfaces: {interfaces}
iinit: {self.iinit}
traits: {self.traits}
'''.format(
    self=self,
    interfaces=interfaces,
)


class StClassInfo(object):

    def __init__(self, stream):
        self.cinit = stream.readEncodedU32()
        trait_count = stream.readEncodedU32()
        self.traits = []
        for _ in range(trait_count):
            self.traits.append(TraitFactory.create(stream))

    def __repr__(self):
        return '<StClassInfo {}>'.format(self.cinit)


class ABCFile(object):

    def __init__(self):
        super(ABCFile, self).__init__()
        self.offset = {}
        self._version = {
            'minor': 0,
            'major': 0,
        }
        self.const_pool = ConstantPool()
        self.methods = []
        self.metadatas = []
        self.instances = []
        self.classes = []
        self.scripts = []
        self.method_bodies = []

    @property
    def version(self):
        return '0x{version.major:02x}.{version.minor:02x}'.format(
            version=self._version
        )

    def parse(self, stream):
        self._version['minor'] = stream.readUI16()
        self._version['major'] = stream.readUI16()
        
        self.offset['const_pool'] = stream.tell()
        self.const_pool.parse(stream)

        self.offset['methods'] = stream.tell()
        self.methods = self._parse_methods(stream)
        self.offset['metadatas'] = stream.tell()
        self.metadatas = self._parse_metadas(stream)
        # parse instance_info && class_info
        self.offset['instances/classes'] = stream.tell()
        class_count = stream.readEncodedU32()
        self.instances = self._parse_instances(stream, class_count)
        self.classes = self._parse_classes(stream, class_count)
        self.offset['scripts'] = stream.tell()
        self.scripts = self._parse_scripts(stream)
        self.offset['method_bodies'] = stream.tell()
        self.method_bodies = self._parse_method_bodies(stream)

    def _parse_methods(self, stream):
        methods = []
        method_count = stream.readEncodedU32()
        for i in range(method_count):
            methods.append(StMethodInfo(stream))
        return methods

    def _parse_metadas(self, stream):
        metadatas = []
        metadata_count = stream.readEncodedU32()
        for _ in range(metadata_count):
            name = stream.readEncodedU32()
            item_count = stream.readEncodedU32()
            items = []
            for j in range(item_count):
                key = stream.readEncodedU32()
                value = stream.readEncodedU32()
                items.append({
                    'key': key,
                    'value': value,
                })
            metadatas.append({
                'name': name,
                'items': items,
            })
        return metadatas

    def _parse_instances(self, stream, class_count):
        instances = []
        for _ in range(class_count):
            instances.append(StInstanceInfo(stream))
        return instances

    def _parse_classes(self, stream, class_count):
        classes = []
        for _ in range(class_count):
            classes.append(StClassInfo(stream))
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
        return bodies
