CC = gcc
CFLAGS = -Wall

SRCS=$(wildcard *.c)

OBJS=$(SRCS:.c=.o)

all: $(OBJS)

${OBJS} : %.o: %.c Makefile
	-$(CC) $(CFLAGS) -c $<
