"""Bounded original arm64 Mach-O parser. File bytes only; no target memory API."""
import hashlib
import struct
import uuid
from pathlib import Path


def need(value, reason):
    if not value: raise ValueError(reason)


class Image:
    def __init__(self, path):
        self.path = Path(path)
        need(self.path.is_absolute() and not any(p.is_symlink() for p in (self.path, *self.path.parents)), 'image path/symlink')
        before = self.path.stat(); need(self.path.is_file() and before.st_size <= 256*1024*1024, 'image file bounds')
        raw = self.path.read_bytes(); after = self.path.stat()
        need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
             (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'image changed')
        self.sha256 = hashlib.sha256(raw).hexdigest(); b = raw
        if raw[:4] == bytes.fromhex('cafebabe'):
            need(len(raw)>=8, 'short fat header')
            count = struct.unpack_from('>I', raw, 4)[0]; need(0<count<=8 and 8+20*count<=len(raw), 'fat bounds')
            matches = [struct.unpack_from('>5I', raw, 8+20*i) for i in range(count)]
            matches = [x for x in matches if x[0] == 0x100000c]; need(len(matches)==1, 'arm64 slice')
            _, _, off, size, _ = matches[0]; need(off+size<=len(raw), 'slice bounds'); b = raw[off:off+size]
        need(len(b)>=32, 'short image'); magic,cpu,_,_,ncmd,cmdsize,_,_=struct.unpack_from('<8I',b)
        need(magic==0xfeedfacf and cpu==0x100000c and ncmd<=200 and 32+cmdsize<=len(b), 'Mach-O bounds/arch')
        self.segments=[];self.uuid=None;self.symbols={};symtab=None;at=32
        for _ in range(ncmd):
            need(at+8<=32+cmdsize, 'command bounds');cmd,size=struct.unpack_from('<II',b,at)
            need(size>=8 and at+size<=32+cmdsize, 'command size')
            if cmd==0x19:
                need(size>=72, 'segment size');vm,vs,fo,fs=struct.unpack_from('<4Q',b,at+24)
                need(fo+fs<=len(b), 'segment bytes');self.segments.append((vm,fs,fo))
            elif cmd==0x1b:
                need(size==24, 'uuid bounds');self.uuid=str(uuid.UUID(bytes=b[at+8:at+24]))
            elif cmd==2:
                need(size>=24, 'symtab command');symtab=struct.unpack_from('<4I',b,at+8)
            at+=size
        need(at==32+cmdsize and self.uuid is not None, 'image UUID/commands');self.b=b
        if symtab:
            off,n,st,ss=symtab;need(n<=300000 and off+16*n<=len(b) and st+ss<=len(b), 'symtab bounds')
            for i in range(n):
                si,typ,section,_,value=struct.unpack_from('<IBBHQ',b,off+16*i)
                if typ&0xe0 or not section:continue
                need(si<ss, 'symbol string');end=b.find(b'\0',st+si,st+ss);need(end!=-1, 'symbol terminator')
                name=b[st+si:end].decode();self.symbols.setdefault(name,set()).add(value)

    def bytes(self, address, count=4):
        need(type(address) is int and type(count) is int and 0<count<=64, 'site bounds')
        matches=[(vm,fo) for vm,sz,fo in self.segments if vm<=address and address+count<=vm+sz]
        need(len(matches)==1, 'site is not unique file-backed bytes');vm,fo=matches[0]
        return self.b[fo+address-vm:fo+address-vm+count]

    def symbol(self, name):
        values=self.symbols.get(name,set());need(len(values)==1, 'symbol absent/ambiguous');return next(iter(values))
