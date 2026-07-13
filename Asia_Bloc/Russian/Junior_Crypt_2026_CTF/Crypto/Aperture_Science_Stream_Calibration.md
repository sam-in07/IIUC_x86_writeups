┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/stream]
└─$ ls                                                              
ciphertext.txt  encoder.py
                                                                                                                                                            
┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/stream]
└─$ cat ciphertext.txt          
1b89ad17b196d415f519f17c9bfa709ac9a7a71605c6d91a7f08fcbb08c2833298388913e843bb0b8bd7bca262207fd861db5440715da4e2916b6245e450df243c6398e0c27fe8d83044b2a4100b83783e65fd27969f9a0adef8decede83339001f71e7fc83a3f7c415c0362d61a28d8d9e83970c840093a0fb6f0a1
                                                                                                

┌──(samin㉿kali)-[~/Downloads/CTF_prac_fiiles/stream]
└─$ python3 

Python 3.13.12 (main, Feb  4 2026, 15:06:39) [GCC 15.2.0] on linux

Type "help", "copyright", "credits" or "license" for more information.

```python
>>> from binascii import unhexlify
... 
... MOD = 1 << 32
... A = 1664525
... C = 1013904223
... 
... cipher = unhexlify(open("ciphertext.txt").read().strip())
... 
... 
... def keystream(seed, length):
...     state = seed & 0xFFFFF
...     out = bytearray()
... 
...     for _ in range(length):
...         state = (A * state + C) % MOD
...         out.append((state >> 24) & 0xFF)
... 
...     return bytes(out)
... 
... 
... def xor(a, b):
...     return bytes(x ^ y for x, y in zip(a, b))
... 
... 
... for seed in range(1 << 20):
... 
...     pt = xor(cipher, keystream(seed, len(cipher)))
... 
...     if b"grodno{" in pt:
...         print("[+] Seed:", seed)
...         print(pt.decode())
...         break
... 
...     # Optional heuristic to speed up spotting readable text
...     if all(32 <= c < 127 or c in (10, 13, 9) for c in pt):
...         try:
...             print(seed, pt.decode())
...         except:
...             pass
...             

```
[+] Seed: 369020
[Aperture Science Internal]
classification=stable
speaker=GLaDOS
memo=grodno{7h15_w45_4_7r1umph_bu7_7h3_533d_w45_700_5m4ll}

>>> 
>>> 






