```python
S = 22263691028918788395010325066307464924652601045336492930678310479674861811846

# n = 2*k + r
# k = S + q
# q = n // 59051
# Therefore:
# q = (2*S + 2*q + r) // 59051

for r in range(2):
    q = (2 * S) // (59051 - 2)

    # Correct the possible rounding boundary
    while (2 * S + 2 * q + r) // 59051 != q:
        q = (2 * S + 2 * q + r) // 59051

    n = 2 * (S + q) + r

    # Verify the telescoped equation
    if n // 2 - n // 59051 == S:
        flag_bytes = n.to_bytes((n.bit_length() + 7) // 8, "big")

        print("n =", n)
        print("flag =", flag_bytes.decode())

```



```markdown
n = 44528890208087634795297285491389256761864239676477679352723497845358270753148
flag = brunner{Pease_porridge_sHOrT_:)|
n = 44528890208087634795297285491389256761864239676477679352723497845358270753149
flag = brunner{Pease_porridge_sHOrT_:)}
```

## brunner{Pease_porridge_sHOrT_:)}