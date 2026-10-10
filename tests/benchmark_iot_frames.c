#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <x86intrin.h>
#include <windows.h>

#include "../include/rubik4d.h"
#include "../include/rubik4d_simd.h"
#include "../include/rubik4d_gcm.h"
#include "../include/aes128.h"
#include "../include/chacha20.h"

static double get_time_sec(void) {
    LARGE_INTEGER freq, counter;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&counter);
    return (double)counter.QuadPart / (double)freq.QuadPart;
}

int main(void) {
    printf("===============================================================================\n");
    printf("  BENCHMARK: SHORT-PACKET IOT TELEMETRY & AEAD FRAME LATENCY EVALUATION\n");
    printf("===============================================================================\n\n");

    const size_t frame_sizes[] = {32, 64, 128, 256, 512, 1024};
    const int num_sizes = sizeof(frame_sizes) / sizeof(frame_sizes[0]);
    const int iterations = 100000;

    uint8_t key16[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
                         0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};
    uint8_t key32[32] = {0};
    memcpy(key32, key16, 16);
    memcpy(key32 + 16, key16, 16);

    uint8_t iv16[16] = {0xca, 0xfe, 0xba, 0xbe, 0xfa, 0xce, 0xdb, 0xad, 0xde, 0xca, 0xf8, 0x88, 0x00, 0x00, 0x00, 0x01};
    uint8_t *iv12 = iv16;
    const char *header_aad = "CoAP/MQTT-SN"; // 12-byte protocol header
    size_t aad_len = strlen(header_aad);

    rubik4d_gcm_ctx gcm_ctx;
    rubik4d_gcm_init(&gcm_ctx, key16, 16);

    rubik4d_ctx tesseract_ctx;
    rubik4d_key_setup(&tesseract_ctx, key16, 16);

    uint8_t aes_rkeys[176];
    aes128_key_expansion(key16, aes_rkeys);

    printf("%-10s | %-12s | %-14s | %-14s | %-14s\n", 
           "Payload", "Tesseract-GCM", "Tesseract-CTR", "Software AES", "ChaCha20");
    printf("%-10s | %-12s | %-14s | %-14s | %-14s\n", 
           "(Bytes)", "(Cycles/Pkt)", "(Cycles/Pkt)", "(Cycles/Pkt)", "(Cycles/Pkt)");
    printf("-------------------------------------------------------------------------------\n");

    for (int s = 0; s < num_sizes; s++) {
        size_t len = frame_sizes[s];
        uint8_t *in_buf = (uint8_t*)malloc(len + 64);
        uint8_t *out_buf = (uint8_t*)malloc(len + 64);
        uint8_t tag[16];
        for (size_t i = 0; i < len; i++) in_buf[i] = (uint8_t)(i & 0xFF);

        // Warm up
        for (int i = 0; i < 1000; i++) {
            rubik4d_gcm_encrypt(&gcm_ctx, iv12, 12, (const uint8_t*)header_aad, aad_len, in_buf, len, out_buf, tag);
        }

        // 1. Tesseract-GCM (Enc + Auth Tag)
        uint64_t c0 = __rdtsc();
        for (int i = 0; i < iterations; i++) {
            rubik4d_gcm_encrypt(&gcm_ctx, iv12, 12, (const uint8_t*)header_aad, aad_len, in_buf, len, out_buf, tag);
        }
        uint64_t c1 = __rdtsc();
        double gcm_cycles_pkt = (double)(c1 - c0) / iterations;

        // 2. Tesseract-CTR (AVX2 parallel)
        c0 = __rdtsc();
        for (int i = 0; i < iterations; i++) {
            rubik4d_ctr_encrypt_avx2(&tesseract_ctx, in_buf, out_buf, len, iv12);
        }
        c1 = __rdtsc();
        double ctr_cycles_pkt = (double)(c1 - c0) / iterations;

        // 3. Software AES-128
        c0 = __rdtsc();
        for (int i = 0; i < iterations; i++) {
            aes128_encrypt(in_buf, len, out_buf, key16, 16, iv12);
        }
        c1 = __rdtsc();
        double aes_cycles_pkt = (double)(c1 - c0) / iterations;

        // 4. ChaCha20
        c0 = __rdtsc();
        for (int i = 0; i < iterations; i++) {
            chacha20_encrypt(in_buf, len, out_buf, key32, 32, iv12);
        }
        c1 = __rdtsc();
        double chacha_cycles_pkt = (double)(c1 - c0) / iterations;

        printf("%-10zu | %10.1f   | %12.1f   | %12.1f   | %12.1f  \n",
               len, gcm_cycles_pkt, ctr_cycles_pkt, aes_cycles_pkt, chacha_cycles_pkt);

        free(in_buf);
        free(out_buf);
    }

    printf("===============================================================================\n");
    return 0;
}
