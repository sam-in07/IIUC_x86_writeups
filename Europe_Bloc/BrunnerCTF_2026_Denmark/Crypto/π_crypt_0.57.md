# π-crypt 0.57 — Writeup

**Category:** Crypto
**Difficulty:** Hard
**Author:** Bond

### Flag

```text
brunner{NB!:_Re-using_the_same_key_without_salting-and-hashing_risks_security_of_all_use-instances,_if_one_instance_leaks_info!}
```

---

## 1. Challenge overview

We are given three files:

```text
baked_pie.txt
bake.py
unbaked_pi.txt
```

The source shows that the flag is encrypted in two stages:

```python
text = flag
text = pie_crypt(text, key)
text = custom_ingredient(text, key)
```

So we need to reverse the operations:

```text
baked_pie.txt
      ↓
custom_ingredient inverse
      ↓
pie_crypt inverse
      ↓
flag
```

The key is unknown, but the source tells us:

```python
assert len(key) == 64
```

---

# 2. The custom alphabet

The challenge uses a custom alphabet:

```python
base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789æøåÆØÅ .,!?-:()[]/{}=<>+_@^|~%$#&*`“';"
```

and:

```python
assert len(base) == 100
```

Therefore every character can be represented by an integer:

```text
A → 0
B → 1
...
```

up to:

```text
99
```

All operations are performed modulo 100.

This makes brute force particularly attractive.

---

# 3. Understanding `custom_ingredient`

The interesting function is:

```python
def custom_ingredient(
    text, key, decrypt=False, rounds=16
):
```

For encryption it starts with:

```python
left, right = text[: len(text) // 2], text[len(text) // 2:]

previous_left = "A" * len(left)
previous_right = "A" * len(right)
```

The key is 64 characters, so the input is split into two 64-character halves.

The important operation is:

```python
def custom_xor(s1, s2, decrypt=False):
    return "".join(
        base[
            (base.index(c1) +
             base.index(c2) *
             (-1 if decrypt else 1))
            % len(base)
        ]
        for c1, c2 in zip(s1, s2)
    )
```

Although this is called `custom_xor`, it is actually modular addition/subtraction.

More importantly, it uses:

```python
zip(s1, s2)
```

So **each character position is independent**.

There is no mixing between character 0 and character 1, character 1 and character 2, etc.

That is the main vulnerability.

---

# 4. Why the 256-byte ciphertext matters

The original `pie_crypt()` output is 128 characters.

The Feistel function returns four 64-character strings:

```python
return "".join(
    round_function(...)
)
```

Therefore the final ciphertext has:

```text
4 × 64 = 256 characters
```

Our file contained:

```text
257 bytes
```

because of the trailing newline:

```text
256 ciphertext characters
+
1 newline
```

After removing the newline:

```text
256
```

We split it into:

```text
C0 = ciphertext[0:64]
C1 = ciphertext[64:128]
C2 = ciphertext[128:192]
C3 = ciphertext[192:256]
```

---

# 5. Reducing the Feistel attack

For each character position `i`, there are only three unknown values:

```text
L[i]
R[i]
K[i]
```

Each is one of the 100 alphabet characters.

Therefore the total search space for one position is:

```text
100 × 100 × 100
= 1,000,000
```

That's very manageable.

We can simulate the Feistel network for every possible:

```text
(L, R, K)
```

and record the resulting four output characters.

Then we compare the result with:

```text
C0[i], C1[i], C2[i], C3[i]
```

The matching combination reveals:

```text
L[i]
R[i]
K[i]
```

We repeat this independently for all 64 positions.

---

# 6. Brute-force lookup

The core of the solver is:

```python
lookup = {}

for k in range(100):
    for x in range(100):
        for y in range(100):
            result = feistel_char(x, y, k)
            lookup.setdefault(result, []).append((x, y, k))
```

This generates exactly:

```text
1,000,000
```

entries.

The solver output confirms:

```text
[+] Lookup entries: 1000000
```

Then for every ciphertext position:

```python
target = (
    chunks[0][pos],
    chunks[1][pos],
    chunks[2][pos],
    chunks[3][pos],
)
```

we perform:

```python
candidates = lookup[target]
```

and recover the original left character, right character, and key character.

---

# 7. Recovering the key

After processing all 64 positions, the solver recovered the complete key:

```text
A_key_can_be_strong_just_by_being_long..._sometimes_at_least_...
```

So the unknown 64-character key has been recovered from the Feistel layer.

At the same time, we recover the original 128-character input to the Feistel layer.

The solver printed:

```text
[+] Input to Feistel / output of pie_crypt:
#)?ybAC/eæv/eT{-xnxb FLp!jP,g,nYø(Z}7`GFF9Fa}y3J31}#E|i$nCWgD!q!tF|*Z2NCQ^`årGpIjåAZT%Ef:1g&^bOTp^v*Ul((6#cNyZcs[Y9Owy4Lø]bTz&øM
```

This is the ciphertext produced by the first encryption stage.

---

# 8. Reversing π-crypt

The original encryption performs:

```python
shift = 10 * d1 + d2

out += base[
    (base.index(c) + shift) % len(base)
]
```

Therefore decryption is simply:

```python
out += base[
    (base.index(c) - shift) % len(base)
]
```

The digits `d1` and `d2` come from `unbaked_pi.txt`.

The initial position is:

```python
i = sum(base.index(c) for c in key)
```

and the key index starts at:

```python
j = 0
```

For every character, we reproduce the exact same state transitions used during encryption.

Since we now know the complete key, we can calculate every π position and every shift.

---

# 9. Final decryption

Running:

```bash
python3 solve.py
```

produced:

```text
[+] Baked ciphertext length: 256
[+] Building Feistel lookup table...
[+] Lookup entries: 1000000

[+] Recovered key:
'A_key_can_be_strong_just_by_being_long..._sometimes_at_least_...'

[+] FLAG:
brunner{NB!:_Re-using_the_same_key_without_salting-and-hashing_risks_security_of_all_use-instances,_if_one_instance_leaks_info!}
```

Therefore the flag is:

```text
brunner{NB!:_Re-using_the_same_key_without_salting-and-hashing_risks_security_of_all_use-instances,_if_one_instance_leaks_info!}
```

---

# 10. What was the actual vulnerability?

The challenge looks complicated because it combines:

* a custom 100-character alphabet
* digits of π
* a 64-character key
* 16 Feistel rounds
* a second encryption layer

But the Feistel implementation doesn't properly mix the entire state.

Because the operations are performed using:

```python
zip(s1, s2)
```

each character position can be attacked independently.

Instead of solving one enormous 64-character cryptographic problem, we solve:

```text
64 independent problems
```

with only:

```text
100³ = 1,000,000
```

possibilities each.

Once the Feistel layer leaks the key, the π-crypt layer becomes trivial to reverse.

---

## Attack chain

```text
                    baked_pie.txt
                          │
                          ▼
                   256 characters
                          │
                 split into 4 × 64
                          │
                          ▼
              Feistel position attack
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
           L + R recovered     64-char key
                 │                 │
                 └────────┬────────┘
                          ▼
                    pie_crypt()
                       inverse
                          │
                          ▼
                        FLAG
```

### Final flag

```text
brunner{NB!:_Re-using_the_same_key_without_salting-and-hashing_risks_security_of_all_use-instances,_if_one_instance_leaks_info!}
```

