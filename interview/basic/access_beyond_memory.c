//gcc -Wall -g test.c -o test.o
//ulimit -c 1000
//gdb test.o  core.3719
#include <stdio.h>

int main(int argc, char *args[])
{
        int i;
	int a[5] = {1,2,3,4,5};
        for (i = 0; i < 6; i++) {
        	printf("a[%d] = %d\n", i, a[i]);
        }
	printf("\na[5] = %d\n", a[5]);
	printf("a[6] = %d\n\n", a[6]);
        a[5] = 10;
	printf("a[5] = %d\n", a[5]);
	printf("a[6] = %d\n", a[6]);
	printf("a[7] = %d\n\n", a[7]);
        for (i = 0; i < 10000; i++) {
        	printf("a[%d] = %d\n", i, a[i]);
        }
        return 0;
}
