from Crypto.Util.number import long_to_bytes

target_sum = 22263691028918788395010325066307464924652601045336492930678310479674861811846
K = 9**5  # 59049

# Estimate n
n_approx = (target_sum * 2 * (K + 2)) // K

# Search locally around n_approx for the exact n
for delta in range(-100, 100):
    n = n_approx + delta
    if (n // 2) - (n // (K + 2)) == target_sum:
        flag_input = long_to_bytes(n).decode()
        print(f"Flag: brunner{{{flag_input}}}")
        break