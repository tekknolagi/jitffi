all: test

testlib.so: test.c
	$(CC) $(CFLAGS) -shared -o testlib.so -fPIC test.c

test: main.py testlib.so
	@python3 main.py

.PHONY: all test
