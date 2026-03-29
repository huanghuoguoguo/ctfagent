#include <stdio.h>
#include <unistd.h>

void pop_rdi_ret(void) {
    __asm__("pop %rdi; ret");
}

void vuln(void) {
    char buf[64];
    puts("payload?");
    read(0, buf, 256);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    puts("ret2libc lab");
    vuln();
    return 0;
}
