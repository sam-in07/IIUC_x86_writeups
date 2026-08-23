
### Encryption logic

For every plaintext character:

```python
chars_to_add = chr(ord(char) + 1) + random_letter_for_confusion
```

So each original character `c` becomes:

```text
next ASCII character + random letter
```

For example:

```text
a → bX
b → cQ
{ → |m
```

The random letter is just noise.

Therefore, to decrypt:

1. Take every **first character** of each 2-character pair.
2. Subtract `1` from its ASCII value.
3. Ignore every second character.

### Given ciphertext

```text
cqsWvloGoWfGsv|LXS4e`YEI4E5EmJuL`ExB2Fuuii`qSV5LoLeUpbnH"W~n
```

Split it into pairs:

```text
cq sW vl oG oW fG sv |L XS 4e `Y EI 4E 5E mJ uL `E xB 2F uu ii `q SV 5L oL eU pb nH "W ~n
```

Take the first character of each pair:

```text
c s v o o f s | X 4 ` E 4 5 m u ` x 2 u i ` S 5 o e p n " ~
```

Now subtract 1 from each ASCII value:

```text
b r u n n e r { W 3 _ D 3 4 l t _ w 1 t h _ R 4 n d o m !
}
```

So the recovered flag is:

```text
brunner{W3_D34lt_w1th_R4ndom!}
```

## Flag

```text
brunner{W3_D34lt_w1th_R4ndom!}
```

The key insight is that **the random letters don't encrypt anything**. They're simply inserted between every encrypted plaintext character, so the ciphertext can be de-interleaved and shifted back by one.
