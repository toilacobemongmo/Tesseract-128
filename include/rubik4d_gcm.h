#ifndef RUBIK4D_GCM_H
#define RUBIK4D_GCM_H

#include "rubik4d.h"
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RUBIK4D_GCM_TAG_SIZE 16
#define RUBIK4D_GCM_IV_DEFAULT_SIZE 12

typedef struct {
    rubik4d_ctx cipher_ctx;
    uint8_t H[16];
    uint8_t H_table[16][256][16];
    int table_ready;
} rubik4d_gcm_ctx;

void rubik4d_gcm_init(rubik4d_gcm_ctx *ctx, const uint8_t *key, size_t key_len);

int rubik4d_gcm_encrypt(rubik4d_gcm_ctx *ctx,
                        const uint8_t *iv, size_t iv_len,
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *plain, size_t plain_len,
                        uint8_t *cipher, uint8_t tag[16]);

int rubik4d_gcm_decrypt(rubik4d_gcm_ctx *ctx,
                        const uint8_t *iv, size_t iv_len,
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *cipher, size_t cipher_len,
                        const uint8_t tag[16], uint8_t *plain);

int rubik4d_aead_encrypt(const uint8_t *key, size_t key_len,
                         const uint8_t *iv, size_t iv_len,
                         const uint8_t *aad, size_t aad_len,
                         const uint8_t *plain, size_t plain_len,
                         uint8_t *cipher, uint8_t tag[16]);

int rubik4d_aead_decrypt(const uint8_t *key, size_t key_len,
                         const uint8_t *iv, size_t iv_len,
                         const uint8_t *aad, size_t aad_len,
                         const uint8_t *cipher, size_t cipher_len,
                         const uint8_t tag[16], uint8_t *plain);

#ifdef __cplusplus
}
#endif

#endif // RUBIK4D_GCM_H
