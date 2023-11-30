
/*
//Lecture #3
//Name: Jihwan Kim 
//Student Number: 2015312911
//page 8

#include <stdio.h>

main()
{
	int a, b, c, d;
	float ratio;

	printf("Enter four integer values\n");
	scanf_s("%d %d %d %d", &a, &b, &c, &d);

	if (c - d != 0) {
		ratio = (float)(a + b) / (float)(c - d);
		printf("Ratio = %f\n", ratio);
	}

	system("pause");
}
*/


/*
//page 13
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define ACCURACY 0.0001
main()
{
	int n, count;
	float x, term, sum;
	printf("Enter value of x:");
	scanf("%f", &x);
	n = term = sum = count = 1;
	while (n <= 100)
	{
		term = term * x / n;
		sum = sum + term;
		if (term < ACCURACY)
			n = 999;
		else
			n = n + 1;
	}

	printf("Terms = %d Sum = %f\n", count, sum);

	system("pause");
}
*/


/*
//page 16
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

main()
{

	float A, B, C;
	printf("Enter three values\n");
	scanf("%f %f %f", &A, &B, &C);
	printf("\n Largest value is ");

	if (A > B)
	{
		if (A > C)
			printf("%f\n", A);
		else
			printf("%f\n", C);
	}
	else
	{
		if (C > B)
			printf("%f\n", C);
		else
			printf("%f\n", B);
	}


	system("pause");
}
*/




/*
//page 20
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int main() {
	int units, custnum;
	float charges;
	printf("Enter CUSTOMER NO. and UNITS cnsumes \n");
	scanf("%d %d", &custnum, &units);
	if (units <= 200)
		charges = 0.5 * units;
	else if (units <= 400)
		charges = 100 + 0.65 * (units - 200);

	else if (units <= 600)
		charges = 230 + 0.8 * (units - 400);
	else
		charges = 390 + (units - 600);

	printf("\n\nCustomer No: %d: Charges = %.2f\n", custnum, charges);
	system("pause");
	return 0;
}
*/


/*
//page 27
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define MAXLOAN 50000

int main() {
	long int loan1, loan2, loan3, sancloan, sum23;
	printf("enter the values of previous two loans:\n");
	scanf("%ld %ld", &loan1, &loan2);
	printf("\n enter the value of new loan:\n");
	scanf("%ld", &loan3);
	sum23 = loan2 + loan3;
	sancloan = (loan1 > 0) ? 0 : ((sum23 > MAXLOAN) ? MAXLOAN - loan2 : loan3);
	printf("\n\n");
	printf("previous loans pending:\n%ld %ld\n", loan1, loan2);
	printf("loan requested = %ld\n", loan3);
	printf("loan sanctioned = %ld\n", sancloan);


	system("pause");
	return 0;
}
*/


/*
//page 31
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>

int main() {
	double x, y;
	int count;
	count = 1;
	printf("Enter FIVE real values in a LINE\n");

read:
	scanf("%lf", &x);
	printf("\n");
	if (x < 0)
		printf("Value - %d is negative\n", count);
	else
	{
		y = sqrt(x);
		printf("%lf\t %lf\n", x, y);
	}

	count = count + 1;
	if (count <= 5)
		goto read;

	printf("\nEnd of computation");

	system("pause");
	return 0;
}
*/





/*
//page 40
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>

int main() {
	int count, n;
	float x, y;

	printf("Enter the values of x and n : ");
	scanf("%f %d", &x, &n);
	y = 1.0;
	count = 1;

	while (count <= n)
	{
		y = y * x;
		count++;
	}

	printf("\nx = %f; n = %d; x to power n = %f\n", x, n, y);

	system("pause");
	return 0;
}
*/
/*output:
Enter the values of x and n : 2.5 4

x = 2.500000; n = 4; x to power n = 39.062500
*/


/*
//page 42
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define COLMAX 10
#define ROWMAX 12

main() {
	int row, column, y;
	row = 1;
	printf("		MULTIPLICATION TABLE		\n");
	printf("-----------------------------------------------\n");
	do
	{
		column = 1;
		do
		{
			y = row * column;
			printf("%4d", y);
			column = column + 1;
		} while (column <= COLMAX);
		printf("\n");
		row = row + 1;
	} while (row <= ROWMAX);
	printf("-------------------------------------------\n");

	system("pause");
}
*/




/*
//page 51
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define FIRST 360
#define SECOND 240


main() {
	int n, m, i, j, roll_number, marks, total;
	printf("Enter number of students and subjects\n");
	scanf("%d %d", &n, &m);
	for (i = 1; i <= n; ++i)
	{
		printf("Enter roll_number : ");
		scanf("%d", &roll_number);
		total = 0;
		printf("\nEnter marks of %d subjects for ROLL NO %d\n", m, roll_number);

		for (j = 1; j <= m; j++) {
			scanf("%d", &marks);
			total = total + marks;
		}
		printf("TOTAL MARKS = %d", total);
		if (total >= FIRST)
			printf("(First Division)\n\n");
		else if (total >= SECOND)
			printf("(Second Division)\n\n");
		else
			printf("(*** F A I L ***\n\n");
	}

	system("pause");
}
*/




/*
//page 57
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define FIRST 360
#define SECOND 240


main() {

	int m;
	float x, sum, average;
	printf("This program computes the average of a set of numbers\n");
	printf("Enter values one after another\n");
	sum = 0;
	for (m = 1; m <= 1000; ++m)
	{
		scanf("%f", &x);
		if (x < 0)
			break;
		sum += x;
	}
	average = sum / (float)(m - 1);
	printf("\n");
	printf("Number of values	= %d\n", m - 1);
	printf("Sum						= %f\n", sum);
	printf("Average					= %f\n", average);

	system("pause");
}
*/



/*
//page 58
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define LOOP 100
#define ACCURACY 0.0001


main() {
	int n;
	float x, term, sum;
	printf("Input value of x : ");
	scanf("%f", &x);
	sum = 0;
	for (term = 1, n = 1; n <= LOOP; ++n)
	{
		sum += term;
		if (term <= ACCURACY)
			goto output;
		term *= x;
	}
	printf("\nFINAL VALUE OF N IS NOT SUFFICIENT\n");
	printf("TO ACHIEVE DESIRED ACCURACY\n");
	goto end;
output:
	printf("\nEXIT FROM LOOP\n");
	printf("Sum = %f; No. of terms = %d\n", sum, n);
	end:
	;
	system("pause");
}
*/



/*
//page 61
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>


main() {
	int count, negative;
	double number, sqroot;
	printf("Enter 9999 to STOP\n");
	count = 0;
	negative = 0;

	while (count <= 100)
	{
		printf("Enter a number : ");
		scanf("%lf", &number);
		if (number == 9999)
			break;
		if (number < 0)
		{
			printf("Number is negative\n\n");
			negative++;
			continue;
		}
		sqroot = sqrt(number);
		printf("Number		= %lf\n Square root = %lf\n\n", number, sqroot);
		printf("\n\nNegative items = %d\n", negative);
		printf("END OF DATA\n");
	}

	system("pause");
}
*/

/*
//Assignment 
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
*/




/*
//page 69
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>


main() {

	int count;
	float value, high, low, sum, average, range;
	sum = 0;
	count = 0;
	printf("Enter numbers in a line : input a NEGATIVE number to end\n");
input:
	scanf("%f", &value);
	if (value < 0)
		goto output;
	count = count + 1;
	if (count == 1)
		high = low = value;
	else if (value > high)
		high = value;
	else if (value < low)
		low = value;
	sum = sum + value;
	goto input;

output:
	average = sum / count;
	range = high - low;
	printf("\n\n");
	printf("Total values : %d\n", count);
	printf("Highest-value: %f\nLowest-value : %f\n", high, low);
	printf("Range		: %f\nAverage : %f\n", range, average);


	system("pause");
}
*/



/*
//page 70
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define CA1 1000
#define CA2 750
#define CA3 500
#define CA4 250
#define EA1 500
#define EA2 200
#define EA3 100
#define EA4 0

main() {
	int level, jobnumber;
	float gross,
		basic,
		house_rent,
		perks,
		net,
		incometax;

input:
	printf("\nEnter level, job number, and basic pay\n");
	printf("Enter 0(zero) for level to END\n\n");
	scanf("%d", &level);

	if (level == 0) goto stop;
	scanf("%d %f", &jobnumber, &basic);

	switch (level)
	{
	case 1:
		perks = CA1 + EA1;
		break;

	case 2:
		perks = CA2 + EA2;
		break;

	case 3:
		perks = CA3 + EA3;
		break;

	case 4:
		perks = CA4 + EA4;
		break;

	default:
		printf("Error in level code\n");
		goto stop;
		break;
	}

	house_rent = 0.25 * basic;
	gross = basic + house_rent + perks;
	if (gross <= 2000)
		incometax = 0;
	else if (gross <= 4000)
		incometax = 0.03 * gross;
	else if (gross <= 5000)
		incometax = 0.05 * gross;
	else
		incometax = 0.08 * gross;
	net = gross - incometax;
	printf("%d %d %.2f\n", level, jobnumber, net);
	goto input;
stop:
	printf("\n\nEND OF THE PROGRAM");

	system("pause");
}
*/


/*
//page 73 - with fix
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define MAX 10

main() {
	int m, x, binom;
	printf(" mx");
	for (m = 0; m <= 10; ++m)
		printf("%4d", m);
	printf("\n--------------------------------------------------\n");
	m = 0;
	do
	{
		printf("%2d ", m);
		x = 0; binom = 1;
		while (x <= m)
		{
			if (m == 0 || x == 0)
				printf("%4d", binom);
			else
			{
				binom = binom * (m - x + 1) / x;
				printf("%4d", binom);
			}
			x = x + 1;

			printf("\n");
			m = m + 1;
		}
	} while (m <= MAX);
	printf("--------------------------------------------------\n");

	system("pause");
}
*/


/*
//pg 75
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#define MAX 10

main() {

	float p, cost, p1, cost1;
	for (p = 0; p <= 10; p = p + 0.1)
	{
		cost = 40 - 8 * p + p * p;
		if (p == 0)
		{
			cost1 = cost;
			continue;
		}
		if (cost >= cost1)
			break;
		cost1 = cost;
		p1 = p;
	}
	p = (p + p1) / 2.0;
	cost = 40 - 8 * p + p * p;
	printf("\nMINIMUM COST = %.2f AT p = %.1f\n", cost, p);

	system("pause");
}
*/


/*
//page 76 - Plotting two functions 
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>

main() {
	int i;
	float a, x, y1, y2;
	a = 0.4;
	printf("				Y---->					\n");
	printf("   0 --------------------------------------\n");
	for (x = 0; x < 5; x = x + 0.25)
	{
		//Evaluation of Functions
		y1 = (int)(50 * exp(-a * x) + 0.5);
		y2 = (int)(50 * exp(-a * x * x / 2) + 0.5);

		//Plotting when y1 = y2
		if (y1 == y2)
		{
			if (x == 2.5)
				printf(" x		|");
			else
				printf(" | ");
			for (i = 1; i <= y1 - 1; ++i)
				printf(" ");
			printf("#\n");
			continue;
		}

		//Plotting when y1 > y2
		if (y1 > y2)
		{
			if (x == 2.5)
				printf("  x  | ");
			else
				printf("     |");
			for (i = 1; i <= y2 - 1; ++i)
				printf(" ");
			printf("*");
			for (i = 1; i <= (y1 - y2 - 1); ++i)
				printf("-");
			printf("O\n");
			continue;
		}

		//Plotting when y2 > y1
		if (x == 2.5)
			printf("  x  |");
		else
			printf("      |");
		for (i = 1; i <= (y1 - 1); ++i)
			printf("  ");
		printf("0");

		for (i = 1; i <= (y2 - y1 - 1); ++i)
			printf("-");
		printf("*\n");

		//End of For Loop
		printf("    |\n");
	}

	system("pause");
}
*/