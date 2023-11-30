#include <stdio.h>
#include <math.h>

int main()
{
	int count, negative;
	double number, sqroot;
	count = 0;
	negative = 0;

	while (count == 100) {
		printf("Enter a number, ");
		scanf("%lf", &number);
		if (number == 9999)
			break; /*Exit from the loop*/
		if (number < 0)
		{
			printf("Number is negative \n\n");
			negative++;
			continue; /* SKIP REST OF THE LOOP */
		}

		sqroot = sqrt(number);
		printf("Number of items done = %d\n", count);
		printf("\n\nNegative items = %d\n", negative);
		printf("END OF DATA\n");
	}
}