```python
content = """# StillAlive — CTF Writeup

### Challenge Overview
We are given two files:
* `public.pem`
* `ciphertexts.json`

The ciphertext file contains the following JSON structure:

```

```text
File written successfully.

```json
{
  "c1": "...",
  "c2": "...",
  "a": 1337,
  "b": 5577100914618608347433571795909361526455637706263378490
}

```

The RSA public key reveals a very small public exponent:

```text
Exponent: 3

```

Using Python to extract parameters:

```python
from Crypto.PublicKey import RSA

key = RSA.import_key(open("public.pem","rb").read())
print(f"n = {key.n}")
print(f"e = {key.e}")

```

Output confirmed:

```text
e = 3

```

---

## Step 1 — Understanding the Vulnerability

The challenge provides:

* Two ciphertexts ($c_1$, $c_2$)
* One RSA modulus ($n$)
* A very small public exponent ($e = 3$)
* Two constants ($a$ and $b$)

This strongly suggests that the underlying plaintexts are **linearly related**.

The encryption relations are:


$$c_1 \equiv m^3 \pmod n$$

$$c_2 \equiv (am+b)^3 \pmod n$$

where $a = 1337$ and $b$ is given. This configuration describes the classic **Franklin–Reiter Related Message Attack**.

---

## Step 2 — Constructing the Polynomials

We work in the polynomial ring $\mathbb{Z}_n[x]$. Define two polynomials:


$$f(x) = x^3 - c_1$$

$$g(x) = (ax+b)^3 - c_2$$

The true plaintext $m$ satisfies:


$$f(m) \equiv 0 \pmod n$$

$$g(m) \equiv 0 \pmod n$$

Therefore, $m$ is a common root of both polynomials over $\mathbb{Z}_n$.

---

## Step 3 — Computing the Polynomial GCD

We compute the Greatest Common Divisor (GCD) of the two polynomials:


$$\gcd(f(x), g(x))$$

For related-message RSA, if $\gcd(f(x), g(x))$ yields a linear polynomial, it takes the form:


$$x - m$$

Once this linear factor is obtained, the plaintext $m$ is simply the negative of the constant term.

---

## Step 4 — Recovering the Plaintext

Converting the recovered integer back into bytes:

```python
from Crypto.Util.number import long_to_bytes

m_bytes = long_to_bytes(m)
print(m_bytes)

```

**Output:**

```text
grodno{571ll_4l1v3_bu7_g14d05_k3375_r3w5171ng_m35s4g35}

```

---

## Flag

```text
grodno{571ll_4l1v3_bu7_g14d05_k3375_r3w5171ng_m35s4g35}

```

---

## Why the Attack Works

RSA assumes every message encrypted under the same public key is independent. Here, the relationship between the two messages is linear and publicly known:


$$m_2 = 1337m + b$$

Because the exponent is small ($e = 3$), both ciphertexts can be expressed as low-degree polynomial equations sharing the same unknown $m$. Computing the polynomial GCD over $\mathbb{Z}_n[x]$ efficiently extracts this shared root.

---

## Intended Vulnerability

* RSA Cryptosystem
* Small public exponent ($e = 3$)
* Linearly related plaintexts
* Franklin–Reiter Related Message Attack

---

## Tools Used

* **Python / PyCryptodome**: To parse `public.pem` and extract $n$ and $e$.
* **SageMath**: To perform polynomial arithmetic and compute $\gcd(f(x), g(x))$ over $\mathbb{Z}_n[x]$.

---

## Summary of the Solution

1. Extract $n$ and $e$ from `public.pem`.
2. Observe $e = 3$ and the constants $a, b$ establishing the relation $m_2 = am + b$.
3. Build the polynomials $f(x) = x^3 - c_1$ and $g(x) = (ax+b)^3 - c_2$.
4. Compute $\gcd(f, g)$ over $\mathbb{Z}_n[x]$.
5. Recover the plaintext integer from the resulting linear factor.
6. Decode the integer to obtain the flag string: `grodno{571ll_4l1v3_bu7_g14d05_k3375_r3w5171ng_m35s4g35}`.
"""

with open("StillAlive_Writeup.md", "w", encoding="utf-8") as f:
f.write(content)
print("File written successfully.")
