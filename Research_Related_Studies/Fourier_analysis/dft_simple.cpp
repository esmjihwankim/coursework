#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <math.h>

void calculateDFT(int len)
{
    int xn[100] = { 0, };
    float Xr[100] = { 0, };
    float Xi[100] = { 0, };
    int i, k, n, N = 0;

    for (i = 0; i < len; i++) {
        printf("Enter the value of x[%d]: ", i);
        scanf("%d", &xn[i]);
    }

    printf("Enter the number of points in the DFT: ");
    scanf("%d", &N);
    for (k = 0; k < N; k++) {
        Xr[k] = 0;
        Xi[k] = 0;
        for (n = 0; n < len; n++) {
            Xr[k] = (Xr[k] + xn[n] * cos(2 * 3.141592 * k * n / N));
            Xi[k] = (Xi[k] - xn[n] * sin(2 * 3.141592 * k * n / N));
        }
        printf("(%f) + j(%f)\n", Xr[k], Xi[k]);
    }
}

int main() {
    int len = 0;
    printf("Enter the length of the sequence: \n");
    scanf("%d4", &len);
    calculateDFT(len);

    return 0;
}