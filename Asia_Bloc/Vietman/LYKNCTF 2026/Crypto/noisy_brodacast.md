  By analyzing the parameters of the encryption:

  1. The message m is relatively small (40 bytes, or 320 bits).
  2. Since the public exponent e = 3, the value of m³ is around 960 bits.
  3. The moduli n₁,n₂,n₃ are all 1024-bit integers (308–309 decimal digits).

  Because m³ < nᵢ for all i, the modulo reduction during RSA encryption did not wrap around the moduli. The three ciphertexts c₁,c₂,c₃ are simply the
  integer C = m³ with different independent noise introduced by the communication channel.

  By converting the ciphertexts to their hexadecimal representations and performing a majority vote on the character at each index, we can correct the
  transmission noise:

  • Index 221: c₁ = '9', c₂ = '9', c₃ = '8' → corrected to '9'
  • Index 225: c₁ = '3', c₂ = '2', c₃ = '2' → corrected to '2'
  • Index 228: c₁ = '5', c₂ = '1', c₃ = '5' → corrected to '5'

  All other hexadecimal digits are identical across the three ciphertexts. Reconstructing the corrected value C and taking its integer cube root yields
  the original message:

    # The recovered message integer m
    m = 3543161048455113947477610052737637847952924194098952402127266683832103525287702220468962293847933

    # m in bytes:
    # b'LYKNCTF{n01sy_CRT_w1th_K4nn4n_3mb3dd1ng}'

  ### Original Plaintext Flag

   LYKNCTF{n01sy_CRT_w1th_K4nn4n_3mb3dd1ng}
