CC ?= gcc
CFLAGS ?= -O3 -Wall -Wextra -Iinclude

TARGET_TEST = test_vectors
TARGET_BENCH = test_benchmark
TARGET_IOT = test_iot_frames

all: $(TARGET_TEST) $(TARGET_BENCH) $(TARGET_IOT)

$(TARGET_TEST): tests/test_vectors.c src/rubik4d.c
	$(CC) $(CFLAGS) -o $@ $^

$(TARGET_BENCH): tests/test_benchmark.c src/rubik4d.c src/aes128.c src/speck128.c src/simon128.c src/chacha20.c
	$(CC) $(CFLAGS) -o $@ $^

$(TARGET_IOT): tests/benchmark_iot_frames.c src/rubik4d.c src/rubik4d_simd.c src/rubik4d_gcm.c src/aes128.c src/chacha20.c
	$(CC) $(CFLAGS) -o $@ $^

test: $(TARGET_TEST)
	./$(TARGET_TEST)

benchmark: $(TARGET_BENCH)
	./$(TARGET_BENCH)

clean:
	rm -f $(TARGET_TEST) $(TARGET_BENCH) $(TARGET_IOT) *.exe *.o
