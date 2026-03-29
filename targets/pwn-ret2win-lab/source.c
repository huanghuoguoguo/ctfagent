#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void win(void) {
    puts("ret2win reached");
    system("/bin/sh");
}

void vuln(void) {
    char buf[64];
    puts("name?");
    read(0, buf, 256);
    printf("hello, %s\n", buf);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    vuln();
    return 0;
}
