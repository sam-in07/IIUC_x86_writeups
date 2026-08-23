# Writeup: Shredded Recipe

**Category:** Cryptography

**Difficulty:** Hard

**Author:** Vincent



---

### Challenge Description

Brunnerne Inc. released a new cake called *citronkvartmåne*—a cost-saving take on the classic *citronhalvmåne*. The recipe was shredded, but we are provided with the source code (`source.py`) and output parameters (`output.txt`).

---

### Challenge Analysis

Inspecting `source.py` reveals how the 54-byte flag is encrypted:

```python
flag = b'brunner{?????????????????????????????????????????????}'
assert len(flag) == 54

p = getPrime(512)

x = bytes_to_long(flag[0::3])
y = bytes_to_long(flag[1::3])
z = bytes_to_long(flag[2::3])

a, b, c = (random.randint(2, p) for _ in range(3))
d = (a*x + b*y + c*z) % p

```

#### Mathematical Properties

1. **Slice Size Bounds:**
The flag is 54 bytes long and split into 3 interwoven slices (`flag[0::3]`, `flag[1::3]`, `flag[2::3]`), meaning each slice contains exactly $54 / 3 = 18$ bytes.


The maximum integer value for an 18-byte array is:

$$B = 256^{18} = 2^{144}$$



Thus, $x, y, z < 2^{144}$.
2. **Hidden Number Problem Formulation:**
We are given $a, b, c, d$ and a 512-bit prime $p \approx 2^{512}$. The variables satisfy:



$$a \cdot x + b \cdot y + c \cdot z \equiv d \pmod p$$



Because $x, y, z \ll p$ (144 bits vs. 512 bits), this system represents a **Small Integer Solution (SIS)** / **Hidden Number Problem (HNP)**. We can formulate this system as a lattice and recover $(x, y, z)$ using **LLL (Lenstra–Lenstra–Lovász) reduction**.

---

### Lattice Construction

We want to find an integer linear combination that yields a short vector containing $(x, y, z)$.

We set up the matrix $M$ such that multiplying by the vector $v = [x, y, z, 1, k]$ (where $a x + b y + c z - d = k \cdot p$) gives a small target vector. To prevent LLL from returning non-zero error vectors modulo $p$, we introduce a large penalty weight factor $K = 2^{256}$.

$$M = \begin{pmatrix} 1 & 0 & 0 & 0 & (a \cdot K) \bmod (p \cdot K) \\ 0 & 1 & 0 & 0 & (b \cdot K) \bmod (p \cdot K) \\ 0 & 0 & 1 & 0 & (c \cdot K) \bmod (p \cdot K) \\ 0 & 0 & 0 & B & (-d \cdot K) \bmod (p \cdot K) \\ 0 & 0 & 0 & 0 & p \cdot K \end{pmatrix}$$

When we multiply $v \cdot M$, we obtain:


$$v \cdot M = [x, y, z, B, (a x + b y + c z - d - k p) \cdot K] = [x, y, z, B, 0]$$

Since $x, y, z < 2^{144}$ and $B = 2^{144}$, the vector $[x, y, z, B, 0]$ has a tiny norm ($\approx 2^{144}$) compared to the lattice determinant ($\approx 2^{512}$). LLL rapidly isolates this unique short vector in sub-second runtime.

---

### Exploitation Script

```python
from Crypto.Util.number import long_to_bytes
from fpylll import IntegerMatrix, LLL

# Given values from output.txt
p = 10647830802868142686934101533552116098730485704268895977393787283804733400028253467785385866485220669299630724611223474820777865812753371976755062912504163
a1 = 5682333430230096023497390561342081513364178815760756537588426222868231923400442457068895501979938328812134382190420455759002208852304897416181437792784805
b1 = 7005110735189986637393390403038676425510033587641886490566466631272351542217810439212990426571730468661879166849471450455770538572793416725422219111440396
c1 = 5699050599188195761952436710701355481375745912226556318938309114236219792866303590000119190534366128772155194033602255642383748128512795914223274121052352
d1 = 8531184132300846595258831618836002845210297909576294925892254278476306366775050239995390218936267367307046890386591236680313055918162376743674035816054950

# Penalty weight and upper bound for 18-byte integers
K = 2**256
B = 2**144

raw_matrix = [
    [1, 0, 0, 0, (a1 * K) % (p * K)],
    [0, 1, 0, 0, (b1 * K) % (p * K)],
    [0, 0, 1, 0, (c1 * K) % (p * K)],
    [0, 0, 0, B, (-d1 * K) % (p * K)],
    [0, 0, 0, 0, p * K],
]

A = IntegerMatrix.from_matrix(raw_matrix)
LLL.reduction(A)

# Inspect reduced basis vectors
for i in range(A.nrows):
    row = [A[i, j] for j in range(A.ncols)]
    if abs(row[3]) == B:
        sign = 1 if row[3] == B else -1
        x, y, z = row[0] * sign, row[1] * sign, row[2] * sign
        
        if x > 0 and y > 0 and z > 0:
            x_b = long_to_bytes(x).rjust(18, b'\x00')
            y_b = long_to_bytes(y).rjust(18, b'\x00')
            z_b = long_to_bytes(z).rjust(18, b'\x00')
            
            # Verify flag structure
            if x_b.startswith(b'b') and z_b.endswith(b'}'):
                flag = bytearray(54)
                flag[0::3] = x_b
                flag[1::3] = y_b
                flag[2::3] = z_b
                print("Flag:", flag.decode())
                break

```

---

### Execution & Output

Executing the script running LLL reduction outputs the decoded flag:

```text
Flag: brunner{i_really_love_solving_equations_with_lattices}

```