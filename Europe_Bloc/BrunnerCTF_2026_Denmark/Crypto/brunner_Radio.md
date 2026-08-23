# Brunner Radio — Writeup

**Challenge:** Brunner Radio
**Category:** Crypto
**Difficulty:** Medium
**Author:** Bond
**Points:** 100

## 1. Challenge Description

The challenge gives us a file called:

```text
broadcast.py
total_broadcast.txt
```

The story says that Brunnerne is broadcasting multiple messages over different frequencies, but all the signals are mixed together.

The important clue is:

> each transmission is broadcast on a different frequency, so the signals can be separated at the receiver end

Our goal is to recover the original transmissions from the mixed broadcast and find the one containing the flag.

---

# 2. Understanding the Source Code

The source tells us there are exactly nine transmissions:

```python
assert len(transmissions) == 9
```

Each transmission is 36 characters:

```python
bytelen_transmission = 36
assert all(len(t) == bytelen_transmission for t in transmissions)
```

Each character is converted into 8-bit binary:

```python
bits = [
    [int(b) for c in t for b in f"{ord(c):08b}"]
    for t in transmissions
]
```

Therefore, every transmission contains:

```text
36 × 8 = 288 bits
```

So there are 288 independent bit positions to recover.

---

# 3. The Different Frequencies

Each transmission gets a wavelength based on its index:

```python
for i in range(len(transmissions)):
    wavelength = i + 1
```

Therefore:

```text
Transmission 1 → wavelength 1
Transmission 2 → wavelength 2
Transmission 3 → wavelength 3
Transmission 4 → wavelength 4
Transmission 5 → wavelength 5
Transmission 6 → wavelength 6
Transmission 7 → wavelength 7
Transmission 8 → wavelength 8
Transmission 9 → wavelength 9
```

The interesting part is:

```python
k = wavelength

while k <= bit_repetition_period:
    smoab[j][k - 1] += bits[i][j]
    k += wavelength
```

The repetition period is:

```python
bit_repetition_period = 100
```

So a transmission with wavelength `w` contributes its bit at positions:

```text
w, 2w, 3w, 4w, ...
```

In other words, transmission `w` contributes whenever the broadcast position is divisible by `w`.

---

# 4. How the Signals Are Mixed

Consider one particular bit position.

Let the original bits be:

```text
b1 b2 b3 b4 b5 b6 b7 b8 b9
```

where `b1` belongs to wavelength 1, `b2` to wavelength 2, etc.

At broadcast position `1`, only wavelength 1 contributes:

```text
y(1) = b1
```

At position `2`, wavelengths 1 and 2 contribute:

```text
y(2) = b1 + b2
```

At position `3`:

```text
y(3) = b1 + b3
```

At position `4`:

```text
y(4) = b1 + b2 + b4
```

At position `6`:

```text
y(6) = b1 + b2 + b3 + b6
```

Generally:

```text
y(k) = Σ b(d), where d divides k
```

This is the key observation.

---

# 5. Recovering the Original Bits

Because the broadcast contains the sum of all bits whose wavelengths divide a position, we can reverse the process.

For wavelength 1:

```text
y(1) = b1
```

Therefore:

```text
b1 = y(1)
```

For wavelength 2:

```text
y(2) = b1 + b2
```

Therefore:

```text
b2 = y(2) - b1
```

For wavelength 3:

```text
y(3) = b1 + b3
```

Therefore:

```text
b3 = y(3) - b1
```

For wavelength 4:

```text
y(4) = b1 + b2 + b4
```

Therefore:

```text
b4 = y(4) - b1 - b2
```

And so on.

Thus, each original bit can be recovered from the broadcast.

---

# 6. Why Only the First 9 Positions Are Needed

There are 100 broadcast positions, but we only need positions 1 through 9.

For example:

```text
position 1 → wavelength 1
position 2 → wavelengths 1, 2
position 3 → wavelengths 1, 3
position 4 → wavelengths 1, 2, 4
...
position 9 → wavelengths 1, 3, 9
```

These positions contain enough information to reconstruct all nine transmissions.

The remaining positions are redundant.

---

# 7. Writing the Decoder

We can directly implement the inverse process.

```python
from pathlib import Path

data = Path("total_broadcast.txt").read_text().splitlines()

assert len(data) == 288
assert all(len(line) == 100 for line in data)

# One recovered bitstream for each wavelength.
transmissions_bits = [[] for _ in range(9)]

for row in data:
    y = [int(x) for x in row]

    recovered = [0] * 9

    for k in range(1, 10):
        value = y[k - 1]

        # Remove contributions from already
        # recovered proper divisors of k.
        for d in range(1, k):
            if k % d == 0:
                value -= recovered[d - 1]

        recovered[k - 1] = value

        assert value in (0, 1)

    for i in range(9):
        transmissions_bits[i].append(recovered[i])


# Convert each bitstream back to ASCII.
transmissions = []

for bits in transmissions_bits:
    text = ""

    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        value = int("".join(map(str, byte)), 2)
        text += chr(value)

    transmissions.append(text)


for i, transmission in enumerate(transmissions, 1):
    print(f"{i}: {transmission}")

for transmission in transmissions:
    if "brunner{" in transmission:
        print("FLAG:", transmission)
```

---

# 8. Running the Solver

Running:

```bash
python3 solve.py
```

produces:

```text
1: hine bright like a diamond. Shine br
2:  takes the shot - and it goes in!! T
3: while other can-openers just open th
4: d. But in my opinion the even better
5: 's going to be cloudy, but sunshine 
6: cause I'm happyyy. Clap along if you
7: brummer{...brrru-uuuuu-uuum-mmmm...}
8: brunner{Brunsviger_is_in_the_air_<3}
9: othello{Sikke_dog_en_dejlig_kage_:D}
```

We can immediately see that transmission 8 contains a valid Brunner flag.

---

# 9. Flag

```text
brunner{Brunsviger_is_in_the_air_<3}
```

---

# 10. Mathematical Explanation

The mixing process can be viewed as a divisor-sum transformation.

For each bit position:

```text
y(n) = Σ b(d), d | n
```

where `b(d)` is the bit transmitted on wavelength `d`.

For example:

```text
y(6) = b(1) + b(2) + b(3) + b(6)
```

Because we know the values of the smaller wavelengths, we can recover the next one:

```text
b(n) = y(n) - Σ b(d)
```

for all proper divisors `d` of `n`.

This is closely related to **Möbius inversion**, although explicitly using Möbius inversion isn't necessary for this challenge.

---

# 11. Final Takeaways

The important observations were:

1. There are **9 transmissions**.
2. Each transmission has **288 bits**.
3. Transmission `i` uses wavelength `i`.
4. A wavelength contributes at every multiple of that wavelength.
5. Therefore, each broadcast value is the **sum of bits whose wavelength divides that position**.
6. The first 9 broadcast positions are sufficient to reconstruct all 9 signals.
7. Convert the recovered bits back into bytes and then ASCII.
8. Search the reconstructed messages for `brunner{`.

The complete attack is therefore:

```text
Mixed broadcast
      ↓
Divisor relationships
      ↓
Recover individual bits
      ↓
288-bit streams
      ↓
8-bit ASCII
      ↓
9 original messages
      ↓
Find brunner{...}
      ↓
brunner{Brunsviger_is_in_the_air_<3}
```

**Flag: `brunner{Brunsviger_is_in_the_air_<3}`**
