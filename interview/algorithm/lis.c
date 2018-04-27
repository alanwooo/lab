/*gcc -Wall -g lis.c  -o lis*/
#include <stdio.h>

const int MAXSIZE = 10;
const int MIN = 0;
int arr[] = { 1, 1, 3, 2, 6, 5 };
int F[] = {0,0,0,0,0,0,0,0,0,0};
int main()
{
    int maxLen = MIN;
    //memset(F, 0, MAXSIZE);
    F[0] = 1;
    for (int i = 1; i < 6; i++)
    {
        for (int j = 0; j < i; j++)
        {
            if (arr[i] > arr[j] && maxLen < F[j])
            {
                maxLen = F[j];
            }
        }

        F[i] = maxLen + 1;
    }

    for (int k = 0; k < 6; k++) {
        printf("%d, ", F[k]);
    }
    printf("\n");
}
