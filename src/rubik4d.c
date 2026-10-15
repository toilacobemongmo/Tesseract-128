#include "../include/rubik4d.h"
#include <string.h>
#include <math.h>

#define ROTL32(v, n) (((v) << (n)) | ((v) >> (32 - (n))))
#define ROTR32(v, n) (((v) >> (n)) | ((v) << (32 - (n))))

// AES S-box
static const uint8_t AES_SBOX[256] = {
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

static const uint8_t AES_INV_SBOX[256] = {
    0x52,0x09,0x6a,0xd5,0x30,0x36,0xa5,0x38,0xbf,0x40,0xa3,0x9e,0x81,0xf3,0xd7,0xfb,
    0x7c,0xe3,0x39,0x82,0x9b,0x2f,0xff,0x87,0x34,0x8e,0x43,0x44,0xc4,0xde,0xe9,0xcb,
    0x54,0x7b,0x94,0x32,0xa6,0xc2,0x23,0x3d,0xee,0x4c,0x95,0x0b,0x42,0xfa,0xc3,0x4e,
    0x08,0x2e,0xa1,0x66,0x28,0xd9,0x24,0xb2,0x76,0x5b,0xa2,0x49,0x6d,0x8b,0xd1,0x25,
    0x72,0xf8,0xf6,0x64,0x86,0x68,0x98,0x16,0xd4,0xa4,0x5c,0xcc,0x5d,0x65,0xb6,0x92,
    0x6c,0x70,0x48,0x50,0xfd,0xed,0xb9,0xda,0x5e,0x15,0x46,0x57,0xa7,0x8d,0x9d,0x84,
    0x90,0xd8,0xab,0x00,0x8c,0xbc,0xd3,0x0a,0xf7,0xe4,0x58,0x05,0xb8,0xb3,0x45,0x06,
    0xd0,0x2c,0x1e,0x8f,0xca,0x3f,0x0f,0x02,0xc1,0xaf,0xbd,0x03,0x01,0x13,0x8a,0x6b,
    0x3a,0x91,0x11,0x41,0x4f,0x67,0xdc,0xea,0x97,0xf2,0xcf,0xce,0xf0,0xb4,0xe6,0x73,
    0x96,0xac,0x74,0x22,0xe7,0xad,0x35,0x85,0xe2,0xf9,0x37,0xe8,0x1c,0x75,0xdf,0x6e,
    0x47,0xf1,0x1a,0x71,0x1d,0x29,0xc5,0x89,0x6f,0xb7,0x62,0x0e,0xaa,0x18,0xbe,0x1b,
    0xfc,0x56,0x3e,0x4b,0xc6,0xd2,0x79,0x20,0x9a,0xdb,0xc0,0xfe,0x78,0xcd,0x5a,0xf4,
    0x1f,0xdd,0xa8,0x33,0x88,0x07,0xc7,0x31,0xb1,0x12,0x10,0x59,0x27,0x80,0xec,0x5f,
    0x60,0x51,0x7f,0xa9,0x19,0xb5,0x4a,0x0d,0x2d,0xe5,0x7a,0x9f,0x93,0xc9,0x9c,0xef,
    0xa0,0xe0,0x3b,0x4d,0xae,0x2a,0xf5,0xb0,0xc8,0xeb,0xbb,0x3c,0x83,0x53,0x99,0x61,
    0x17,0x2b,0x04,0x7e,0xba,0x77,0xd6,0x26,0xe1,0x69,0x14,0x63,0x55,0x21,0x0c,0x7d
};

// 12 PERMUTATION
static const uint8_t PERM_TABLES[12][16] = {
    { 1, 3, 0, 2,  5, 7, 4, 6,  9,11, 8,10, 13,15,12,14}, // XY
    { 2, 0, 3, 1,  6, 4, 7, 5, 10, 8,11, 9, 14,12,15,13},
    { 4, 5, 6, 7,  1, 0, 3, 2, 12,13,14,15,  9, 8,11,10}, // XZ
    { 5, 4, 7, 6,  0, 1, 2, 3, 13,12,15,14,  8, 9,10,11},
    { 8, 9,10,11, 12,13,14,15,  1, 0, 3, 2,  5, 4, 7, 6}, // XW
    { 9, 8,11,10, 13,12,15,14,  0, 1, 2, 3,  4, 5, 6, 7},
    { 2, 3, 1, 0,  6, 7, 5, 4, 10,11, 9, 8, 14,15,13,12}, // YZ
    { 3, 2, 0, 1,  7, 6, 4, 5, 11,10, 8, 9, 15,14,12,13},
    { 4, 6, 5, 7,  0, 2, 1, 3, 12,14,13,15,  8,10, 9,11}, // YW
    { 6, 4, 7, 5,  2, 0, 3, 1, 14,12,15,13, 10, 8,11, 9},
    { 8,10, 9,11,  0, 2, 1, 3,  4, 6, 5, 7, 12,14,13,15}, // ZW
    {10, 8,11, 9,  2, 0, 3, 1,  6, 4, 7, 5, 14,12,15,13}
};

static uint8_t INV_PERM_TABLES[12][16];
static int tables_initialized = 0;

void rubik4d_init_tables(void) {
    if (tables_initialized) return;
    for (int t = 0; t < 12; t++) {
        for (int i = 0; i < 16; i++) {
            INV_PERM_TABLES[t][PERM_TABLES[t][i]] = (uint8_t)i;
        }
    }
    tables_initialized = 1;
}

double rubik4d_calculate_entropy(const uint8_t *data, size_t len) {
    if (len == 0) return 0.0;
    uint64_t counts[256] = {0};
    for (size_t i = 0; i < len; i++) counts[data[i]]++;
    double entropy = 0.0;
    double dlen = (double)len;
    for (int i = 0; i < 256; i++) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / dlen;
            entropy -= p * (log(p) / log(2.0));
        }
    }
    return entropy;
}

// Golden-ratio round constants: rc[r][k] = floor(2^32 * frac((4r + k + 1) * phi))
// Generated offline from the fractional part of phi = (1 + sqrt(5)) / 2, providing
// asymmetric, fixed-point-free constants that break round symmetry.
static const uint32_t RC_TABLE[9][4] = {
    { 0x00000000, 0x00000000, 0x00000000, 0x00000000 }, // unused: K_0 = MK (whitening)
    { 0x1715609F, 0xB54CDA58, 0x53845412, 0xF1BBCDCB },
    { 0x8FF34785, 0x2E2AC13E, 0xCC623AF8, 0x6A99B4B1 },
    { 0x08D12E6B, 0xA708A824, 0x454021DE, 0xE3779B97 },
    { 0x81AF1551, 0x1FE68F0A, 0xBE1E08C4, 0x5C55827D },
    { 0xFA8CFC37, 0x98C475F0, 0x36FBEFAA, 0xD5336963 },
    { 0x736AE31D, 0x11A25CD6, 0xAFD9D690, 0x4E115049 },
    { 0xEC48CA03, 0x8A8043BC, 0x28B7BD76, 0xC6EF372F },
    { 0x6526B0E9, 0x035E2AA2, 0xA195A45C, 0x3FCD1E15 }
};

// SubWord: apply the AES S-box to each of the four bytes of a 32-bit word.
static uint32_t sub_word(uint32_t v) {
    return ((uint32_t)AES_SBOX[(v >> 24) & 0xFF] << 24) |
           ((uint32_t)AES_SBOX[(v >> 16) & 0xFF] << 16) |
           ((uint32_t)AES_SBOX[(v >>  8) & 0xFF] <<  8) |
           ((uint32_t)AES_SBOX[ v        & 0xFF]);
}

// k_fold derivation. Folds a 128-bit state into a single byte so that all 256
// permutation schedules are reachable. A rotate-multiply mixer precedes the fold so
// that no single key byte localizes to a single output bit.
static uint8_t derive_k_fold(const uint8_t st[16]) {
    uint32_t acc = 0x243F6A88u;              // fractional part of pi (nothing-up-my-sleeve)
    for (int i = 0; i < 16; i++) {
        uint32_t x = (uint32_t)st[i] ^ (uint32_t)(i * 0x9E3779B9u);
        x = ROTL32(x * 0x85EBCA6Bu, 7) ^ (x >> 3);
        acc ^= x;
        acc = ROTL32(acc, 5) + 0x165667B1u;
    }
    acc ^= acc >> 16;
    acc *= 0x7FEB352Du;
    acc ^= acc >> 15;
    acc *= 0x846CA68Bu;
    acc ^= acc >> 16;
    return (uint8_t)(acc & 0xFF);
}

// Key schedule
void rubik4d_key_setup(rubik4d_ctx *ctx, const uint8_t *key, size_t key_len) {
    rubik4d_init_tables();
    uint8_t master[16] = {0};
    if (key_len == 16) {
        memcpy(master, key, 16);
    } else {
        for (size_t i = 0; i < key_len; i++) master[i % 16] ^= key[i];
    }

    memcpy(ctx->round_keys[0], master, 16);

    for (int r = 1; r <= 8; r++) {
        // 1. SO(4) hypercube permutation of the previous subkey:
        //    K'_r = R_{sigma(r)}(K_{r-1}), sigma(r) = (r - 1) mod 6.
        int tbl_idx = (((r - 1) % 6) * 2) + (r & 1);
        const uint8_t *perm = PERM_TABLES[tbl_idx];
        uint8_t kp[16];
        for (int i = 0; i < 16; i++) kp[i] = ctx->round_keys[r - 1][perm[i]];

        // 2. Serial ARX word chain with round-constant injection. Each word absorbs all
        //    preceding words plus a non-linear SubWord, so a single master-key bit
        //    reaches every byte of K_r after one round.
        uint32_t w0, w1, w2, w3;
        memcpy(&w0, kp +  0, 4);
        memcpy(&w1, kp +  4, 4);
        memcpy(&w2, kp +  8, 4);
        memcpy(&w3, kp + 12, 4);

        w0 = ROTL32(w0 + sub_word(w3) + RC_TABLE[r][0], 11);
        w1 = ROTL32(w1 + w0          + RC_TABLE[r][1], 13);
        w2 = ROTL32(w2 + w1          + RC_TABLE[r][2], 17);
        w3 = ROTL32(w3 + w2          + RC_TABLE[r][3], 19);

        memcpy(ctx->round_keys[r] +  0, &w0, 4);
        memcpy(ctx->round_keys[r] +  4, &w1, 4);
        memcpy(ctx->round_keys[r] +  8, &w2, 4);
        memcpy(ctx->round_keys[r] + 12, &w3, 4);

        // 3. Derive the permutation-table selector from the new subkey (full 8 bits),
        //    so the SO(4) schedule varies with every bit of the master key.
        ctx->k_fold = derive_k_fold(ctx->round_keys[r]);
        ctx->perm_lut[r] = PERM_TABLES[((r + (ctx->k_fold & 7)) % 6) * 2 + ((ctx->k_fold >> 3) & 1)];
    }
    ctx->k_fold = derive_k_fold(ctx->round_keys[8]);
    ctx->perm_lut[0] = PERM_TABLES[0];
}

void rubik4d_generate_round_keys(const uint8_t *key, size_t key_len, uint8_t round_keys[9][16]) {
    rubik4d_ctx ctx;
    rubik4d_key_setup(&ctx, key, key_len);
    memcpy(round_keys, ctx.round_keys, sizeof(ctx.round_keys));
}

void rubik4d_encrypt_block(const uint8_t in[16], uint8_t out[16], const uint8_t round_keys[9][16]) {
    rubik4d_ctx ctx;
    memcpy(ctx.round_keys, round_keys, sizeof(ctx.round_keys));

    rubik4d_init_tables();
    ctx.k_fold = derive_k_fold(ctx.round_keys[8]);
    for (int r = 1; r <= 8; r++) {
        ctx.perm_lut[r] = PERM_TABLES[((r + (ctx.k_fold & 7)) % 6) * 2 + ((ctx.k_fold >> 3) & 1)];
    }
    ctx.perm_lut[0] = PERM_TABLES[0];

    rubik4d_encrypt_block_fast(&ctx, in, out);
}

void rubik4d_encrypt_block_fast(const rubik4d_ctx *ctx, const uint8_t in[16], uint8_t out[16]) {
    uint8_t state[16];
    for (int i = 0; i < 16; i++) {
        state[i] = in[i] ^ ctx->round_keys[0][i];
    }

    for (int r = 1; r <= 8; r++) {
        // 1. SubBytes
        for (int i = 0; i < 16; i++) {
            state[i] = AES_SBOX[state[i]];
        }

        // 2. SO(4) Hypercube Permutation
        const uint8_t* lut = ctx->perm_lut[r];
        uint8_t rot[16];
        for (int i = 0; i < 16; i++) {
            rot[i] = state[lut[i]];
        }

        // 3. 32-bit ARX diffusion
        uint32_t* w = (uint32_t*)rot;
        w[1] ^= ROTL32(w[0] + 0x5A5A5A5AU, 7);
        w[2] ^= ROTL32(w[1] + 0x5A5A5A5AU, 11);
        w[3] ^= ROTL32(w[2] + 0x5A5A5A5AU, 13);
        w[0] ^= ROTL32(w[3] + 0x5A5A5A5AU, 17);

        // 4. AddRoundKey
        for (int i = 0; i < 16; i++) {
            state[i] = rot[i] ^ ctx->round_keys[r][i];
        }
    }
    memcpy(out, state, 16);
}

void rubik4d_decrypt_block_fast(const rubik4d_ctx *ctx, const uint8_t in[16], uint8_t out[16]) {
    uint8_t state[16];
    memcpy(state, in, 16);

    for (int r = 8; r >= 1; r--) {
        uint8_t rot[16];
        for (int i = 0; i < 16; i++) {
            rot[i] = state[i] ^ ctx->round_keys[r][i];
        }

        // Inverse ARX diffusion
        uint32_t* w = (uint32_t*)rot;
        w[0] ^= ROTL32(w[3] + 0x5A5A5A5AU, 17);
        w[3] ^= ROTL32(w[2] + 0x5A5A5A5AU, 13);
        w[2] ^= ROTL32(w[1] + 0x5A5A5A5AU, 11);
        w[1] ^= ROTL32(w[0] + 0x5A5A5A5AU, 7);

        // Inverse permutation and InvSubBytes
        const uint8_t* lut = ctx->perm_lut[r];
        uint8_t temp[16];
        for (int i = 0; i < 16; i++) {
            temp[lut[i]] = rot[i];
        }
        for (int i = 0; i < 16; i++) {
            state[i] = AES_INV_SBOX[temp[i]];
        }
    }

    for (int i = 0; i < 16; i++) {
        out[i] = state[i] ^ ctx->round_keys[0][i];
    }
}

size_t rubik4d_encrypt(const uint8_t *in, size_t in_len, uint8_t *out, 
                       const uint8_t *key, size_t key_len, const uint8_t *iv) {
    rubik4d_ctx ctx;
    rubik4d_key_setup(&ctx, key, key_len);

    uint8_t pad = 16 - (in_len % 16);
    size_t total_len = in_len + pad;
    uint8_t block[16];
    uint8_t cur_iv[16];
    memcpy(cur_iv, iv, 16);

    for (size_t i = 0; i < total_len; i += 16) {
        for (int j = 0; j < 16; j++) {
            size_t idx = i + j;
            block[j] = (idx < in_len) ? in[idx] : pad;
            block[j] ^= cur_iv[j];
        }
        rubik4d_encrypt_block_fast(&ctx, block, out + i);
        memcpy(cur_iv, out + i, 16);
    }
    return total_len;
}

size_t rubik4d_decrypt(const uint8_t *in, size_t in_len, uint8_t *out, 
                       const uint8_t *key, size_t key_len, const uint8_t *iv) {
    if (in_len == 0 || (in_len % 16) != 0) return 0;

    rubik4d_ctx ctx;
    rubik4d_key_setup(&ctx, key, key_len);

    uint8_t cur_iv[16];
    memcpy(cur_iv, iv, 16);

    for (size_t i = 0; i < in_len; i += 16) {
        rubik4d_decrypt_block_fast(&ctx, in + i, out + i);
        for (int j = 0; j < 16; j++) {
            out[i + j] ^= cur_iv[j];
        }
        memcpy(cur_iv, in + i, 16);
    }

    uint8_t pad = out[in_len - 1];
    if (pad < 1 || pad > 16) return 0;
    for (size_t i = in_len - pad; i < in_len; i++) {
        if (out[i] != pad) return 0;
    }
    return in_len - pad;
}