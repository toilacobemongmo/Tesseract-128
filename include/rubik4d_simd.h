#ifndef RUBIK4D_SIMD_H
#define RUBIK4D_SIMD_H

#include "rubik4d.h"
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// CPU feature detection
int rubik4d_has_ssse3(void);
int rubik4d_has_avx2(void);
int rubik4d_has_pclmul(void);

// SSSE3 single-block permutation
void rubik4d_encrypt_block_simd(const rubik4d_ctx *ctx, const uint8_t in[16], uint8_t out[16]);
void rubik4d_decrypt_block_simd(const rubik4d_ctx *ctx, const uint8_t in[16], uint8_t out[16]);

// AVX2 4-block parallel CTR mode
void rubik4d_ctr_encrypt_avx2(const rubik4d_ctx *ctx, const uint8_t *in, uint8_t *out, size_t len, const uint8_t iv[16]);

#ifdef __cplusplus
}
#endif

#endif // RUBIK4D_SIMD_H
