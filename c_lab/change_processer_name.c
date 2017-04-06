/*
 * Change the process name in the runtime
 */

#include<stdio.h> 
#include <string.h> 

int main(int argc, char *argv[]) 
{ 
    int i = 0; 
    char buff[100]; 

    memset(buff,0,sizeof(buff)); 

    strncpy(buff, argv[0], sizeof(buff)); 
    memset(argv[0], 0, strlen(buff)); 

    strncpy(argv[0], "NewName", 7); 

    // Simulate a wait. Check the process 
    // name at this point.
    sleep(10);
    // for(;i<0xffffffff;i++); 
    return 0; 
}

