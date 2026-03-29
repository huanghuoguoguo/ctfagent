CC := gcc
CFLAGS := -O0 -g -fno-stack-protector -no-pie
TARGET := chall

all: $(TARGET)

$(TARGET): source.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

.PHONY: all clean
