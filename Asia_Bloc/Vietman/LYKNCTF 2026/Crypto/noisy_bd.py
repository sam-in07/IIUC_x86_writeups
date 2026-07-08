from collections import Counter

c1 = 258513173341110907855004634578328776675613337727374937778021308566776511394028586169719647601517686407530370600703671047834514223488817495300633613007122903215194800830817082508335094056353114537752319982589386027924378028160153097890317313131416661071211651623002925590879169419712047717
c2 = 258513173341110907855004634578328776675613337727374937778021308566776511394028586169719647601517686407530370600703671047834514223488817495300633613007122903215194800830817082508335094056353114537752319982589386027924378028160153097890317313131416661071211651623002925590874661422038166117
c3 = 258513173341110907855004634578328776675613337727374937778021308566776511394028586169719647601517686407530370600703671047834514223488817495300633613007122903215194800830817082508335094056353114537752319982589386027924378028160153097890317313131416661071211651623002925295726760640731851365

h1 = hex(c1)[2:]
h2 = hex(c2)[2:]
h3 = hex(c3)[2:]

# Check lengths
assert len(h1) == len(h2) == len(h3)

corrected_hex = []
for i in range(len(h1)):
    chars = [h1[i], h2[i], h3[i]]
    # Get the most common character
    most_common = Counter(chars).most_common(1)[0][0]
    corrected_hex.append(most_common)

corrected_hex_str = "".join(corrected_hex)
print(f"Corrected hex: {corrected_hex_str}")

C = int(corrected_hex_str, 16)

# We want to find the integer cube root of C.
# Using a simple binary search for cube root:
def iroot(k, n):
    u, s = n, n+1
    while u < s:
        s = u
        u = ((k-1)*s + n//(s**(k-1)))//k
    return s

m = iroot(3, C)
print(f"C: {C}")
print(f"m^3: {m**3}")
print(f"Does m^3 == C? {m**3 == C}")

if m**3 == C:
    # Convert m to bytes
    try:
        from crypto.Util.number import long_to_bytes
    except ImportError:
        # manual long_to_bytes
        def long_to_bytes(val):
            s = hex(val)[2:]
            if len(s) % 2 != 0:
                s = '0' + s
            return bytes.fromhex(s)
            
    plaintext = long_to_bytes(m)
    print(f"Plaintext: {plaintext}")
    print(f"Plaintext decoded: {plaintext.decode('utf-8', errors='ignore')}")
else:
    print("Failed to recover correct cube root!")
