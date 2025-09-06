# Crypto Challenge: Xor

**Hint**: The flag is XOR-encrypted. Key is an integer between 1-255.

## Solution Script
```python
def xor_decrypt(ciphertext, key):
    return ''.join(chr(ord(c) ^ 143) for c in ciphertext)
xor_decrypt(encrypted_flag, 143)
```
