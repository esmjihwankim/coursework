#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>

main() {
	int i;
	int positiveExponent, negativeExponent;
	float toPowerN;
	float toInversePowerN;

	printf("--------------------------------------------------------\n");
	printf(" 2 to power n \t n \t 2 to power -n\n");
	printf("--------------------------------------------------------\n");



	for (i = 0; i <= 20; i++) {

		positiveExponent = 0;
		negativeExponent = 0;

		toPowerN = pow(2, i);
		toInversePowerN = pow(2, -i);

		//convert 2 to power n to exponential form
		while (toPowerN > 10)
		{
			toPowerN = toPowerN / 10.0;
			positiveExponent++;
		}

		//convert 2 to power -n to exponential form
		while (toInversePowerN < 1)
		{
			toInversePowerN *= 10;
			negativeExponent++;
		}

		if (negativeExponent != 0) {
			negativeExponent = -negativeExponent;
		}


		printf("%8.3f e %d \t", toPowerN, positiveExponent);
		printf("%2d \t", i);
		printf("%8.3f e %d \n", toInversePowerN, negativeExponent);

	}

	system("pause");
}