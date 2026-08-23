
### Writeup logic

The important observation was the 160-byte block at offset `0x9d20`:

```text
00 03 03 03 00 00 03 03 ...
```

It contains only two values:

```text
0x00
0x03
```

Treating those as binary:

```text
0x00 → 0
0x03 → 1
```

produces:

```text
01110011 01110100 01110010 01101111 ...
```

Grouping into 8-bit bytes gives ASCII:

```text
01110011 = s
01110100 = t
01110010 = r
01101111 = o
01101110 = n
01100111 = g
...
```

Your script correctly recovered:

```text
b'strong_force_in_you\x00'
```

The trailing `\x00` is just a null terminator, so the flag text is:

```text
strong_force_in_you
```

### Final submission

```text
brunner{strong_force_in_you}
```


