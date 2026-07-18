# 01_CORE/Makefile - El Martillo del Artesano
CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
TARGET = neurobit_pulse

all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $(TARGET) main.c

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)