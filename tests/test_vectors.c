#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "rubik4d.h"

static void print_hex(const char *label, const uint8_t *data, size_t len) {
    printf("%-18s: ", label);
    for (size_t i = 0; i < len; ++i) {
        printf("%02X ", data[i]);
    }
    printf("\n");
}

static void run_vector(int id, const char *desc, const uint8_t *key, const uint8_t *pt) {
    rubik4d_ctx ctx;
    uint8_t ct[16];
    uint8_t decrypted[16];

    printf("[Test Vector %d: %s]\n", id, desc);
    print_hex("Key", key, 16);
    print_hex("Plaintext", pt, 16);

    rubik4d_key_setup(&ctx, key, 16);
    rubik4d_encrypt_block_fast(&ctx, pt, ct);
    print_hex("Ciphertext (8R)", ct, 16);

    rubik4d_decrypt_block_fast(&ctx, ct, decrypted);
    print_hex("Decrypted", decrypted, 16);

    if (memcmp(pt, decrypted, 16) == 0) {
        printf("Verification      : PASS (Decryption matches Plaintext)\n\n");
    } else {
        printf("Verification      : FAIL\n\n");
    }
}

int main(void) {
    rubik4d_init_tables();

    uint8_t key1[16] = {0};
    uint8_t pt1[16]  = {0};
    run_vector(1, "All-Zero Input (Extreme Boundary)", key1, pt1);

    uint8_t key2[16] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F
    };
    uint8_t pt2[16] = "Rubik4D Cipher!!";
    run_vector(2, "Incremental Key with ASCII Plaintext", key2, pt2);

    return 0;
}