// gcc -Wall -g str_to_int.c -o str_to_int
// gdb str_to_int
#include <stdio.h>
#include <string.h>

int str_to_int(char *c)
{
	int num = 0;
	if(!c)
	{
		return num;
	}
	if(c)
	{
		while(*c != '\0')
		{
			num = num * 10 + *c - '0';
			c++;
		}
	}
	return num;
}

int main(int argc, char *args[])
{
	//char *c = NULL;
	char *c = "12r1123";
	int ret = 0;
	ret = str_to_int(c);
	printf("string:%s\nint:%d\n", c, ret);
	printf("%x\n",*c);
	return 0;
}
