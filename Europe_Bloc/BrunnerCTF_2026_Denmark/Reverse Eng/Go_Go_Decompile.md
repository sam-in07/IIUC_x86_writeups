# Go Go Decompile — Writeup

**Category:** Reverse Engineering
**Difficulty:** Easy


## 1. Challenge Overview

We are given a Go executable called:

```bash
go_go_budgetmaster
```

Running it asks for a license key:

```text
Go Go License? AAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Incorrect!
Are you sure you work here?
```

The goal is to recover the correct license/flag from the binary.

---

## 2. Initial Enumeration

First, inspect the file:

```bash
ls -l
file go_go_budgetmaster
```

The binary is a Go executable. Since Go is not installed on the system, commands such as:

```bash
go tool nm ./go_go_budgetmaster
```

are unavailable.

However, we can still analyze the binary using standard Linux tools and GDB.

---

## 3. Searching for Interesting Strings

Use `strings` to look for the challenge messages:

```bash
strings -t x ./go_go_budgetmaster | grep -Ei 'Go Go License|Incorrect|Are you sure'
```

This reveals:

```text
Go Go License?
Incorrect!
Are you sure you work here?
```

We also notice that the binary contains:

```text
Correct!
This is way better than Excel!
```

So there is clearly a success path hidden in the executable.

---

## 4. Inspecting the Go Binary

Checking the ELF sections:

```bash
readelf -S ./go_go_budgetmaster | grep -E 'gopclntab|go.build|text|rodata'
```

gives:

```text
.text
.rodata
.gopclntab
.go.buildinfo
```

The presence of `.gopclntab` is a strong indication that this is a Go binary and that useful symbol/function information may still be available.

---

## 5. Using GDB/Pwndbg

Start the binary with GDB:

```bash
gdb ./go_go_budgetmaster
```

Since this is a Go binary, we can directly set a breakpoint on `main.main`:

```gdb
break main.main
run
```

GDB identifies:

```text
Breakpoint 1 at 0x4a1f96: file gogo/gogo.go, line 9.
```

This is useful because we now have the actual Go function responsible for the license check.

Disassembling it:

```gdb
disassemble main.main
```

shows an important sequence.

---

## 6. Understanding the License Check

The program first reads our input using a scanner:

```asm
call   bufio.(*Scanner).Scan
```

Then retrieves the entered text:

```asm
call   bufio.(*Scanner).Text
```

The next interesting part is:

```asm
mov    rax,QWORD PTR [rip + 0xbe49c]
call   encoding/base64.(*Encoding).DecodedLen
```

and later:

```asm
call   encoding/base64.(*Encoding).Decode
```

This tells us that the input is **Base64 decoded** before being checked.

The program then eventually reaches:

```asm
call   runtime.memequal
```

`runtime.memequal` is Go's internal byte/string comparison function.

The relevant logic is effectively:

```text
user input
    ↓
Base64 decode
    ↓
compare decoded data
    ↓
Correct / Incorrect
```

---

## 7. Finding the Hardcoded Value

Earlier in `main.main`, we see:

```asm
lea    rdx,[rip + 0x2aa2c]
```

which resolves to:

```text
0x4cc9e8
```

Let's inspect that address:

```gdb
x/s 0x4cc9e8
```

The result contains:

```text
YnJ1bm5lcntnMF9kM2MwbXAxbDNkX2cwX2Jycn0=Correct!
This is way better than Excel!
```

The first part is the interesting Base64 string:

```text
YnJ1bm5lcntnMF9kM2MwbXAxbDNkX2cwX2Jycn0=
```

The `Correct!` text immediately following it is simply another embedded string in `.rodata`.

---

## 8. Decode the Base64

We can decode the value directly:

```bash
echo 'YnJ1bm5lcntnMF9kM2MwbXAxbDNkX2cwX2Jycn0=' | base64 -d
```

Output:

```text
brunne{g0_d3c0mp1l3d_g0_brr}
```

Therefore, the flag is:

```text
brunne{g0_d3c0mp1l3d_g0_brr}
```

---

## 9. Verification

We can verify the discovered value by running the binary and entering it:

```bash
./go_go_budgetmaster
```

Enter:

```text
brunne{g0_d3c0mp1l3d_g0_brr}
```

The program should reach:

```text
Correct!
This is way better than Excel!
```

---

## 10. Key Takeaways

The challenge is straightforward once the Go binary is inspected:

* `strings` reveals useful embedded strings.
* `.gopclntab` indicates a Go executable.
* GDB can identify `main.main` even without installing Go.
* The input is Base64 decoded.
* `runtime.memequal` performs the final comparison.
* The expected value is stored directly in the binary as Base64.
* Decoding that value gives the flag.

### Final Flag

```text
brunne{g0_d3c0mp1l3d_g0_brr}
```
