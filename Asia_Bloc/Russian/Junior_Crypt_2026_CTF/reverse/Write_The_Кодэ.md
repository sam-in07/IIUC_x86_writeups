Problem : 

Author: @hckerror
hard

Usually, by changing the environment, people mean going on vacation, but I prefer to change the compiler.

Will be useful

./tcc -B./runtime checker.c -o checker
./checker

Flag format: grodno{[a-z0-9_]+} Обычно под сменой обстановки люди имеют ввиду сьездить на отдых, я же предпочитаю сменить компилятор

Вам пригодится

./tcc -B./runtime checker.c -o checker
./checker

Time : 5:14 pm

Find Flag : 8:35 pm 


Soln :



---

# Writeup:  Write The "Кодэ"

## Challenge Description

The challenge provides:

* A custom TinyCC compiler (`tcc`)
* A runtime directory
* A C source file:

```c
#include <stdio.h>
#include <string.h>

/* Our build system links this from the internal audit library. */
extern int audit(const char *answer);

int main(void)
{
    char answer[128];

    puts("Build provenance check");

    fputs("receipt: ", stdout);

    if (!fgets(answer, sizeof answer, stdin))
        return 1;

    answer[strcspn(answer, "\n")] = 0;

    puts(audit(answer) ? "accepted" : "rejected");

    return 0;
}
```

The goal is to recover the correct input:

```
grodno{[a-z0-9_]+}
```

---

# 1. Understanding the Hint

The challenge title says:

> Usually, by changing the environment, people mean going on vacation, but I prefer to change the compiler.

This hints that the important part is not the C file itself but the custom compiler environment.

The build command is:

```bash
./tcc -B./runtime checker.c -o checker
```

The `-B` option tells TinyCC to use a custom runtime directory.

---

# 2. Inspecting the Files

First list everything:

```bash
find . -type f
```

Output:

```
runtime/libtcc1.a
runtime/include/*
checker.c
tcc
```

The runtime contains only the normal TinyCC runtime.

Check for `audit`:

```bash
nm -A runtime/* 2>/dev/null | grep audit
```

No result.

Therefore:

* `audit()` is not inside `libtcc1.a`
* the custom logic is likely injected by the compiler

---

# 3. Compile the Binary

Build:

```bash
./tcc -B./runtime checker.c -o checker
```

Run:

```bash
./checker
```

Test:

```
receipt: AAAAA
```

Result:

```
rejected
```

---

# 4. Inspect the Binary

The binary is stripped:

```bash
nm checker
```

Output:

```
nm: checker: no symbols
```

So use GDB.

Start:

```bash
gdb ./checker
```

or:

```bash
pwndbg ./checker
```

---

# 5. Find main()

Inside GDB:

```gdb
disassemble main
```

We see:

```asm
0x401f27:
call 0x402292
```

This is the call to `audit()`.

The interesting part:

```asm
0x401f27: lea rax,[rbp-0x80]
0x401f2a: call 0x402292
```

The function at:

```
0x402292
```

is the hidden checker.

---

# 6. Reverse the Audit Function

Disassemble:

```gdb
disassemble 0x402292,+400
```

Important observations:

## It checks length

```asm
call strlen
cmp rax,0x60
```

Maximum length:

```
0x60 = 96 bytes
```

---

## It allocates executable memory

```asm
call mmap
```

A 512-byte buffer is created:

```asm
mov eax,0x200
```

---

## It decrypts data

The function copies bytes from:

```
0x405b34
```

and decrypts them.

Important:

```asm
call 0x40220c
```

generates a key stream.

The decrypted data is stored in:

```
mmap buffer
```

---

## It changes permissions

```asm
call mprotect
```

The buffer becomes executable.

---

# 7. Break After Decryption

Set breakpoint after mprotect:

```gdb
b *0x4023cb
```

Run:

```gdb
run
```

Enter anything:

```
a
```

When stopped:

Get decrypted buffer address:

```gdb
set $buf = *(void **)($rbp-0x10)
```

View bytes:

```gdb
x/32bx $buf
```

Output:

```
0x7ffff7fbb000:
0x33 0x00 0x51 0xa7 ...
```

This confirms successful decryption.

---

# 8. Dump Decrypted Data

Dump the memory:

```gdb
dump binary memory decrypted.bin $buf $buf+0x200
```

Exit GDB.

Check:

```bash
ls
```

Now:

```
checker
checker.c
decrypted.bin
runtime
tcc
```

---

# 9. Analyze the Decrypted Format

View:

```bash
xxd -g 1 decrypted.bin
```

Beginning:

```
33 00 51 a7 ...
```

Meaning:

```
33 00
```

Length:

```
0x33 = 51
```

Then:

```
51
```

Magic byte.

The rest is a table.

Each entry:

```
a7
<addition byte>
<rotation>
<expected DWORD>
```

The checker performs:

```
state = 0xc0dec0de
```

For each character:

1. Add input character
2. XOR state
3. Rotate bits
4. Mix with:

```
0x45d9f3b
0x9e3779b9
```

5. Compare against stored DWORD

---

# 10. Recover the Flag

Create:

```bash
nano solve.py
```

Use the inverse algorithm:

```python
import struct

data=open("decrypted.bin","rb").read()

length=struct.unpack("<H",data[:2])[0]

state=0xc0dec0de
pos=3
flag=[]

def ror32(x,n):
    return ((x>>n)|(x<<(32-n))) & 0xffffffff


for i in range(length):

    assert data[pos]==0xa7
    pos+=1

    add=data[pos]
    pos+=1

    rot=data[pos]&0x1f
    pos+=1

    expected=struct.unpack("<I",
        data[pos:pos+4])[0]

    pos+=4


    x=(expected-
       ((i*0x45d9f3b)^0x9e3779b9)) & 0xffffffff


    x=ror32(x,rot)


    c=((x^state)-add)&0xff

    flag.append(chr(c))


    state=(state^(c+add))&0xffffffff


print("".join(flag))
```

Run:

```bash
python3 solve.py
```

Output:

```
grodno{Fabrice_Bellard_is_a_really_cool_programmer}

```

That is the flag.

---

# Final Notes

The main trick of this challenge is that:

* `checker.c` contains no validation logic.
* `audit()` is injected by the custom compiler.
* The checker code is hidden inside encrypted data.
* GDB is used to catch the decrypted memory after runtime unpacking.
* The decrypted table can then be reversed mathematically.

The important commands used:

```bash
find . -type f

./tcc -B./runtime checker.c -o checker

nm -A runtime/* | grep audit

gdb ./checker

disassemble main

disassemble 0x402292,+400

b *0x4023cb

run

set $buf = *(void **)($rbp-0x10)

x/32bx $buf

dump binary memory decrypted.bin $buf $buf+0x200

xxd -g 1 decrypted.bin

python3 solve.py
```

This completes the full solve chain.






==================
 pwndbg> disassemble 0x402292,+400
Dump of assembler code from 0x402292 to 0x402422:

 0x00000000004023cb:  mov    rax,QWORD PTR [rbp-0x10]

pwndbg> b *0x4023cb
Breakpoint 1 at 0x4023cb
pwndbg> run
Starting program: /home/samin/Downloads/CTF_prac_fiiles/dist/checker 
⚠️ warning: Probes-based dynamic linker interface failed.
Reverting to original interface.
Build provenance check
receipt: a

Breakpoint 1, 0x00000000004023cb in ?? ()
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
───────────────────────────────────────────────────────────────────────[ LAST SIGNAL ]───────────────────────────────────────────────────────────────────────
Breakpoint hit at 0x4023cb
───────────────────────────────────────────────────[ REGISTERS / show-flags off / show-compact-regs off ]────────────────────────────────────────────────────
 RAX  0
 RBX  0
 RCX  0x7ffff7ebaaa7 ◂— cmp rax, -0xfff
 RDX  5
 RDI  0x7ffff7fbb000 ◂— xor eax, dword ptr [rax] /* '3' */
 RSI  0x200
 R8   0xffffffff
 R9   0
 R10  5
 R11  0x246
 R12  1
 R13  0x7ffff7ffd000 (_rtld_global) —▸ 0x7ffff7ffe2f0 ◂— 0
 R14  0x7fffffffdd88 —▸ 0x7fffffffe11b ◂— 'COLORFGBG=15;0'
 R15  0x7ffff7ffe2f0 ◂— 0
 RBP  0x7fffffffdbd0 —▸ 0x7fffffffdc60 —▸ 0x7fffffffdd78 —▸ 0x7fffffffe0e8 ◂— '/home/samin/Downloads/CTF_prac_fiiles/dist/checker'
 RSP  0x7fffffffdb80 ◂— 0
 RIP  0x4023cb ◂— mov rax, qword ptr [rbp - 0x10]
────────────────────────────────────────────────────────────[ DISASM / x86-64 / set emulate on ]─────────────────────────────────────────────────────────────
b► 0x4023cb    mov    rax, qword ptr [rbp - 0x10]     RAX, [0x7fffffffdbc0] => 0x7ffff7fbb000 ◂— xor eax, dword ptr [rax] /* '3' */
   0x4023cf    movzx  eax, byte ptr [rax]             EAX, [0x7ffff7fbb000] => 0x33
   0x4023d2    mov    rcx, qword ptr [rbp - 0x10]     RCX, [0x7fffffffdbc0] => 0x7ffff7fbb000 ◂— xor eax, dword ptr [rax] /* '3' */
   0x4023d6    add    rcx, 1                          RCX => 0x7ffff7fbb001 (0x7ffff7fbb000 + 0x1)
   0x4023da    movzx  ecx, byte ptr [rcx]             ECX, [0x7ffff7fbb001] => 0
   0x4023dd    shl    rcx, 8
   0x4023e1    or     rax, rcx                        RAX => 0x33 (0x33 | 0x0)
   0x4023e4    mov    qword ptr [rbp - 0x20], rax     [0x7fffffffdbb0] <= 0x33
   0x4023e8    mov    rax, qword ptr [rbp - 0x20]     RAX, [0x7fffffffdbb0] => 0x33
   0x4023ec    cmp    rax, 8                          0x33 - 0x8     EFLAGS => 0x216 [ cf PF AF zf sf IF df of iopl:00 ac ]
   0x4023f0  ✘ jb     0x40241b                    <0x40241b>
──────────────────────────────────────────────────────────────────────────[ STACK ]──────────────────────────────────────────────────────────────────────────
00:0000│ rsp 0x7fffffffdb80 ◂— 0
01:0008│-048 0x7fffffffdb88 —▸ 0x405d33 ◂— 0xf935c000000000a2
02:0010│-040 0x7fffffffdb90 —▸ 0x7ffff7fbb1ff ◂— add byte ptr [rax], al
03:0018│-038 0x7fffffffdb98 ◂— 0xc0dec0deffffdd88
04:0020│-030 0x7fffffffdba0 —▸ 0x7ffff7ffe2f0 ◂— 0
05:0028│-028 0x7fffffffdba8 ◂— 0x200
06:0030│-020 0x7fffffffdbb0 ◂— 9 /* '\t' */
07:0038│-018 0x7fffffffdbb8 ◂— 0xfaac1d00657f3050
────────────────────────────────────────────────────────────────────────[ BACKTRACE ]────────────────────────────────────────────────────────────────────────
 ► 0         0x4023cb None
   1         0x401f2f main+158
   2   0x7ffff7dd2f77 None
   3   0x7ffff7fc6000 None
   4         0x401e91 main
   5      0x1ffffdd60 None
   6   0x7fffffffdd78 None
   7              0x0 None
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
pwndbg> set $buf = *(void **)($rbp-0x10)
pwndbg> x/32bx $buf
0x7ffff7fbb000: 0x33    0x00    0x51    0xa7    0x31    0x01    0x46    0xfa
0x7ffff7fbb008: 0xf4    0x1f    0xa7    0x7a    0x08    0xa1    0x90    0x65
0x7ffff7fbb010: 0x8f    0xa7    0xc3    0x0f    0x81    0x0f    0x56    0x5f
0x7ffff7fbb018: 0xa7    0x0c    0x16    0x8b    0x79    0x87    0x8f    0xa7
pwndbg> dump binary memory decrypted.bin $buf $buf+0x200
pwndbg> 








┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/dist]
└─$ xxd -g 1 decrypted.bin
00000000: 33 00 51 a7 31 01 46 fa f4 1f a7 7a 08 a1 90 65  3.Q.1.F....z...e
00000010: 8f a7 c3 0f 81 0f 56 5f a7 0c 16 8b 79 87 8f a7  ......V_....y...
00000020: 55 1d 7e f4 31 a1 a7 9e 05 12 14 22 b2 a7 e7 0c  U.~.1......"....
00000030: fd cd 5d a5 a7 30 13 12 4e 15 ed a7 79 1a 9c d5  ..]..0..N...y...
00000040: 8f e0 a7 c2 02 8d 33 bd 3b a7 0b 09 6e 22 07 30  ......3.;...n".0
00000050: a7 54 10 37 de 05 d1 a7 9d 17 6c 92 3c 46 a7 e6  .T.7......l.<F..
00000060: 1e 0f 91 85 78 a7 2f 06 e1 2c 8e c4 a7 78 0d 5d  ....x./..,...x.]
00000070: a6 d6 a4 a7 c1 14 73 d7 a8 53 a7 0a 1b 0a 32 9e  ......s..S....2.
00000080: fe a7 53 03 4e e1 93 c5 a7 9c 0a ee 77 4c 1c a7  ..S.N.......wL..
00000090: e5 11 bd 41 d9 b6 a7 2e 18 af 4f 50 f5 a7 77 1f  ...A......OP..w.
000000a0: 67 fe e4 f8 a7 c0 07 70 df dd 6c a7 09 0e 68 af  g......p..l...h.
000000b0: b4 6e a7 52 15 0f cc 41 ee a7 9b 1c 16 6f 99 2e  .n.R...A.....o..
000000c0: a7 e4 04 d2 97 7f d5 a7 2d 0b 78 82 c4 e0 a7 76  ........-.x....v
000000d0: 12 28 f3 3b eb a7 bf 19 37 49 a6 2e a7 08 01 22  .(.;....7I....."
000000e0: c4 ad 76 a7 51 08 4f 3e 49 c3 a7 9a 0f c6 60 d5  ..v.Q.O>I.....`.
000000f0: ad a7 e3 16 c7 d1 83 6b a7 2c 1d d1 36 6c 14 a7  .......k.,..6l..
00000100: 75 05 97 e4 a3 90 a7 be 0c 48 23 1b 7e a7 07 13  u........H#.~...
00000110: 54 cc ae 55 a7 50 1a 77 f3 ca 21 a7 99 02 79 62  T..U.P.w..!...yb
00000120: c3 b7 a7 e2 09 39 55 90 b3 a7 2b 10 a7 19 0f 7f  .....9U...+.....
00000130: a7 74 17 dc 4e ce e3 a7 bd 1e 99 bb 13 57 a7 06  .t..N........W..
00000140: 06 7b 84 32 1f a7 4f 0d 09 c9 7e a7 a7 98 14 58  .{.2..O...~....X
00000150: ba d1 d3 a7 e1 1b 81 30 59 46 a7 2a 03 dc 84 a5  .......0YF.*....
00000160: 7e a7 73 0a 39 12 8f da 00 00 00 00 00 00 00 00  ~.s.9...........
00000170: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000180: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
00000190: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001a0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001b0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001c0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001d0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001e0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
000001f0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................

┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/dist]
└─$ python3            
Python 3.13.12 (main, Feb  4 2026, 15:06:39) [GCC 15.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> #!/usr/bin/env python3
... import struct
... 
... data = open("decrypted.bin", "rb").read()
... 
... length = struct.unpack("<H", data[:2])[0]
... 
... state = 0xc0dec0de
... pos = 3
... flag = []
... 
... def ror32(x, n):
...     x &= 0xffffffff
...     return ((x >> n) | (x << (32-n))) & 0xffffffff
... 
... for i in range(length):
...     assert data[pos] == 0xa7
...     pos += 1
... 
...     add = data[pos]
...     pos += 1
... 
...     rot = data[pos] & 0x1f
...     pos += 1
... 
...     expected = struct.unpack("<I", data[pos:pos+4])[0]
...     pos += 4
... 
...     # undo state += mix
...     x = (expected - ((i * 0x45d9f3b) ^ 0x9e3779b9)) & 0xffffffff
... 
...     # undo rotate
...     x = ror32(x, rot)
... 
...     # undo xor
...     c = ((x ^ state) - add) & 0xff
... 
...     flag.append(chr(c))
... 
...     # forward update state to verify next byte
...     state = (state ^ (c + add)) & 0xffffffff
...     state = ((state << rot) | (state >> (32-rot))) & 0xffffffff
...     state = (state + ((i * 0x45d9f3b) ^ 0x9e3779b9)) & 0xffffffff
... 
... print("".join(flag))
... 
grodno{Fabrice_Bellard_is_a_really_cool_programmer}
>>> 
