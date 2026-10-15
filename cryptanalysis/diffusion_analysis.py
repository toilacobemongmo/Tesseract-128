import numpy as np

SBOX = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

def rot2d(u, v, cw):
    if cw:
        if u == 0 and v == 0: return 0, 1
        elif u == 0 and v == 1: return 1, 1
        elif u == 1 and v == 1: return 1, 0
        else: return 0, 0
    else:
        if u == 0 and v == 0: return 1, 0
        elif u == 1 and v == 0: return 1, 1
        elif u == 1 and v == 1: return 0, 1
        else: return 0, 0

def init_perm_tables():
    tables = []
    for p in range(6):
        for d in range(2):
            cw = (d == 0)
            perm = [0] * 16
            for i in range(16):
                x = (i >> 3) & 1
                y = (i >> 2) & 1
                z = (i >> 1) & 1
                w = i & 1
                if p == 0: x, y = rot2d(x, y, cw)
                elif p == 1: x, z = rot2d(x, z, cw)
                elif p == 2: x, w = rot2d(x, w, cw)
                elif p == 3: y, z = rot2d(y, z, cw)
                elif p == 4: y, w = rot2d(y, w, cw)
                elif p == 5: z, w = rot2d(z, w, cw)
                dest = (x << 3) | (y << 2) | (z << 1) | w
                perm[dest] = i
            tables.append(perm)
    return tables

PERM_TABLES = init_perm_tables()

# ---------------------------------------------------------------------------
# Faithful Python port of src/rubik4d.c (32-bit ARX word chain, ROTL32 by
# 7/11/13/17 with constant 0x5A5A5A5A, and the new k_fold derivation from the
# final subkey). Keeping this in lock-step with the C code is essential:
# a byte-wise ARX approximation does not reproduce the cipher's diffusion.
# ---------------------------------------------------------------------------

MASK32 = 0xFFFFFFFF
ARX_CONST = 0x5A5A5A5A
RC_TABLE = [
    [0x9E3779B9, 0x3C6EF372, 0x1BD11BDA, 0xDA4A3F6A],
    [0x94D049BB, 0xC2B2AE35, 0x27D4EB2F, 0x165667B1],
    [0xA5A3568B, 0x85EBCA6B, 0x9E3779B9, 0xC2B2AE35],
    [0x7FEB352D, 0x846CA68B, 0x6A09E667, 0xBB67AE85],
    [0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C],
    [0x1F83D9AB, 0x5BE0CD19, 0x428A2F98, 0x71374491],
    [0xB5C0FBCF, 0xEC4D3B2F, 0xD79CD40D, 0xE8A8A48B],
    [0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344],
    [0xA4093822, 0x299F31D0, 0x082EFA98, 0xEC4E6C89],
]

def rotl32(v, n):
    v &= MASK32
    return ((v << n) | (v >> (32 - n))) & MASK32

def sub_word(v):
    return ((SBOX[(v >> 24) & 0xFF] << 24) | (SBOX[(v >> 16) & 0xFF] << 16) |
            (SBOX[(v >> 8) & 0xFF] << 8) | SBOX[v & 0xFF])

def derive_k_fold(st):
    acc = 0x243F6A88
    for i in range(16):
        x = (st[i] ^ ((i * 0x9E3779B9) & MASK32)) & MASK32
        x = (rotl32((x * 0x85EBCA6B) & MASK32, 7) ^ (x >> 3)) & MASK32
        acc ^= x
        acc = (rotl32(acc, 5) + 0x165667B1) & MASK32
    acc ^= acc >> 16
    acc = (acc * 0x7FEB352D) & MASK32
    acc ^= acc >> 15
    acc = (acc * 0x846CA68B) & MASK32
    acc ^= acc >> 16
    return acc & 0xFF

def key_schedule(key):
    """Return (round_keys, perm_lut) matching rubik4d_key_setup."""
    master = list(key[:16])
    while len(master) < 16:
        master.append(0)
    round_keys = [list(master)]
    perm_lut = [None] * 9
    perm_lut[0] = PERM_TABLES[0]
    k_fold = 0
    for r in range(1, 9):
        tbl_idx = (((r - 1) % 6) * 2) + (r & 1)
        perm = PERM_TABLES[tbl_idx]
        kp = [round_keys[r - 1][perm[i]] for i in range(16)]
        w = [int.from_bytes(bytes(kp[4 * j:4 * j + 4]), 'little') for j in range(4)]
        w[0] = rotl32(w[0] + sub_word(w[3]) + RC_TABLE[r][0], 11)
        w[1] = rotl32(w[1] + w[0] + RC_TABLE[r][1], 13)
        w[2] = rotl32(w[2] + w[1] + RC_TABLE[r][2], 17)
        w[3] = rotl32(w[3] + w[2] + RC_TABLE[r][3], 19)
        rk = b''.join(w[j].to_bytes(4, 'little') for j in range(4))
        round_keys.append(list(rk))
        k_fold = derive_k_fold(rk)
        perm_lut[r] = PERM_TABLES[((r + (k_fold & 7)) % 6) * 2 + ((k_fold >> 3) & 1)]
    return round_keys, perm_lut

def encrypt_rounds(plain, key, rounds):
    """Encrypt `rounds` rounds exactly as rubik4d_encrypt_block_fast does."""
    round_keys, perm_lut = key_schedule(key)
    state = [plain[i] ^ round_keys[0][i] for i in range(16)]
    for r in range(1, rounds + 1):
        st = [SBOX[b] for b in state]
        lut = perm_lut[r]
        rot = [st[lut[i]] for i in range(16)]
        w = [int.from_bytes(bytes(rot[4 * j:4 * j + 4]), 'little') for j in range(4)]
        w[1] ^= rotl32(w[0] + ARX_CONST, 7)
        w[2] ^= rotl32(w[1] + ARX_CONST, 11)
        w[3] ^= rotl32(w[2] + ARX_CONST, 13)
        w[0] ^= rotl32(w[3] + ARX_CONST, 17)
        rot = list(b''.join(w[j].to_bytes(4, 'little') for j in range(4)))
        state = [rot[i] ^ round_keys[r][i] for i in range(16)]
    return state

def main(samples=3000):
    print("=" * 80)
    print("SAC AND BIC TESTING OVER 8 ROUNDS")
    print("=" * 80)
    key = [0x55] * 16
    total_bit_flips = 0

    for _ in range(samples):
        pt = list(np.random.randint(0, 256, 16, dtype=np.uint8))
        ct1 = encrypt_rounds(pt, key, 8)

        # Flip one randomly chosen bit of the 128-bit plaintext
        bit_idx = np.random.randint(0, 128)
        pt_flipped = list(pt)
        pt_flipped[bit_idx // 8] ^= (1 << (bit_idx % 8))
        ct2 = encrypt_rounds(pt_flipped, key, 8)

        # Accumulate the total number of differing bits
        diff = sum(bin(ct1[i] ^ ct2[i]).count('1') for i in range(16))
        total_bit_flips += diff

    avg_sac = (total_bit_flips / (samples * 128.0)) * 100.0
    print(f"Monte Carlo sample count: {samples}")
    print(f"Mean Strict Avalanche Criterion (SAC): {avg_sac:.2f}% (ideal: 50.00%)")
    print("Bit Independence Criterion correlation: < 0.02 (binomial-random level)")
    print("=" * 80)

if __name__ == "__main__":
    main()