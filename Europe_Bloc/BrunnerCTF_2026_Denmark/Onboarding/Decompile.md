# CTF Write-up — **Decompile?**

### Challenge Name

**Decompile?**

### Category

Reverse Engineering

### Objective

Analyze the provided `vault` binary, determine the values expected by the program, and submit them in the correct order to obtain the success message.

---

## 1. Initial Analysis

The challenge provides an ELF binary named:

```text
vault
```

I started by loading it into `gdb` with `pwndbg`:

```bash
gdb ./vault
```

The first useful step was to inspect the `main` function:

```gdb
disassemble main
```

The binary contains a large amount of `puts()` calls, which initially makes the function look much more complicated than it actually is.

After the introductory output, the program repeatedly calls an `ask` function to obtain user input and then performs comparisons on that input.

---

## 2. Finding the Password

The first important section was:

```asm
lea    rdx,[rip+0xf00]        # 0x555555556435
lea    rax,[rbp-0x50]
mov    rsi,rdx
mov    rdi,rax
call   strcmp@plt
test   eax,eax
je     ...
```

This tells us that the user's first input is compared using `strcmp()` against the string located at:

```text
0x555555556435
```

Instead of guessing, I inspected that address directly:

```gdb
x/s 0x555555556435
```

This revealed:

```text
"Pl4nt3xt_p455w0rd_1s_bu551ng"
```

Therefore the password is:

```text
Pl4nt3xt_p455w0rd_1s_bu551ng
```

---

## 3. Finding the Staplers Value

The next input is converted to an integer using:

```asm
call   __isoc23_strtol@plt
```

The resulting value is then compared against:

```asm
cmp    rax,0xfef
je     ...
```

Convert hexadecimal `0xfef` to decimal:

```text
0xfef = 4079
```

The program subsequently stores this value in:

```asm
mov    QWORD PTR [rip+0x39ed],rax
# 0x5555555590e0 <badge_staplers>
```

So:

```text
badge_staplers = 4079
```

---

## 4. Finding the Asset Tag

The next input is again converted using `strtol`.

The important comparison is:

```asm
cmp    rax,0x2a
je     ...
```

`0x2a` in decimal is:

```text
0x2a = 42
```

The value is then stored in:

```asm
mov    QWORD PTR [rip+0x389d],rax
# 0x5555555590e8 <badge_asset_tag>
```

Therefore:

```text
badge_asset_tag = 42
```

---

## 5. Finding the Mug Letter

The next check is slightly different because the program checks individual bytes:

```asm
movzx  eax,BYTE PTR [rbp-0x50]
cmp    al,0x42
jne    ...
movzx  eax,BYTE PTR [rbp-0x4f]
test   al,al
je     ...
```

The first byte must equal:

```text
0x42
```

ASCII `0x42` is:

```text
B
```

The following byte must be zero, meaning the input must simply be the single character:

```text
B
```

The program then stores that character in:

```asm
mov    BYTE PTR [rip+0x3761],al
# 0x5555555590f0 <badge_mug_letter>
```

---

## 6. Finding the Budget

The final numeric input is converted with `strtol`:

```asm
call   __isoc23_strtol@plt
```

Then the value is doubled:

```asm
add    rax,rax
```

and compared against:

```asm
cmp    rax,0x5dc
```

Convert `0x5dc`:

```text
0x5dc = 1500
```

Therefore:

```text
input × 2 = 1500
```

So:

```text
input = 750
```

The program then divides the value by two before storing it:

```asm
mov    rax,QWORD PTR [rbp-0x58]
mov    rdx,rax
shr    rdx,0x3f
add    rax,rdx
sar    rax,1
mov    QWORD PTR [rip+0x35ac],rax
# 0x5555555590f8 <badge_budget>
```

Thus:

```text
badge_budget = 750
```

---

# 7. Final Answers

The required inputs, in order, are:

```text
Pl4nt3xt_p455w0rd_1s_bu551ng
4079
42
B
750
```

| Input      |                 Required value | Reason                |
| ---------- | -----------------------------: | --------------------- |
| Password   | `Pl4nt3xt_p455w0rd_1s_bu551ng` | `strcmp()` comparison |
| Staplers   |                         `4079` | `0xfef`               |
| Asset Tag  |                           `42` | `0x2a`                |
| Mug Letter |                            `B` | `0x42` ASCII          |
| Budget     |                          `750` | `750 × 2 = 0x5dc`     |

After entering these values, the challenge accepted the submission.

---

## 8. Useful GDB Commands

The most useful commands during the solve were:

```gdb
disassemble main
```

to inspect the program logic,

```gdb
x/s 0x555555556435
```

to inspect the password string,

and:

```gdb
p/x &badge_staplers
p/x &badge_asset_tag
p/x &badge_mug_letter
p/x &badge_budget
```

to locate the global variables.

Their addresses were:

```text
badge_staplers   = 0x5555555590e0
badge_asset_tag  = 0x5555555590e8
badge_mug_letter = 0x5555555590f0
badge_budget     = 0x5555555590f8
```

The key lesson from this challenge is that the huge `main()` function is mostly distraction/output. The actual validation logic consists of a handful of `strcmp`, `strtol`, byte comparisons, and arithmetic checks. Once those checks are translated from assembly into simple conditions, the solution becomes straightforward.

### Flag / Submission

```text
Pl4nt3xt_p455w0rd_1s_bu551ng
4079
42
B
750
```

**Result: Submission Accepted.**
