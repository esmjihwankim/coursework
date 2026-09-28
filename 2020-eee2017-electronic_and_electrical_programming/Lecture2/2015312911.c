/*
Assignment #2
Name: Jihwan Kim (±Ë¡ˆ»Ø)
Student Number: 2015312911
*/


/*page 18*/
/*
 * Converts distanes from miles to kilometers.
 */
#include <stdio.h> /* printf, scanf definitions */
#define KMS_PER_MILE 1.609 /* Conversion Constant  */

int main(void)
{
	double miles, kms;

	/* Get the dsitance in miles. */
	printf("Enter the distance in miles ");
	scanf_s("%lf", &miles);

	/* Convert the distance to kilmeters. */
	kms = KMS_PER_MILE * miles;

	/* Display the distance in kilometers. */
	printf("The equals %f kilometers. \n", kms);

	system("pause");
	return 0;
}
/*Output:
Enter the distance in miles 20
The equals 32.180000 kilometers.
*/




/*page19*/
#include <stdio.h>

void main(void)
{
	char my_char;
	printf("Please type a character: ");
	my_char = getchar();
	printf("\nYou have typed this character: ");
	putchar(my_char);

	system("pause");
}
/*output:
Please type a character: 7

You have typed this character: 7
*/


/*page 32*/
#include <stdio.h>

void main(void)
{
	int months, days;

	printf("Enter days\n");
	scanf_s("%d", &days);

	months = days / 30;
	days = days % 30;
	printf("Months = %d Days = %d", months, days);

	system("pause");
}
/*output:
Enter days
265
Months = 8 Days = 25*/



/*page 39*/
#include <stdio.h>
#define N 100
#define A 2 

main()
{
	int a;
	a = A;
	while (a < N)
	{
		printf("%d\n", a);
		a *= a;
	}

	system("pause");
}
/*output:
2
4
16
*/


/*page 59*/
 /*-------------Sum of n terms of 1/n------------ */
#include <stdio.h>

main()
{
	float sum, n, term;
	int count = 1;

	sum = 0;
	printf("enter value of n\n");
	scanf_s("%f", &n);
	term = 1.0 / n;
	while (count <= n)
	{
		sum = sum + term;
		count++;
	}

	printf("Sum = %f\n", sum);
	system("pause");
}
/*output:
enter value of n
99
Sum = 1.000001*/