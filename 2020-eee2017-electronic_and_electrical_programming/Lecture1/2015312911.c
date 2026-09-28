/* 
Name: Jihwan Kim (±Ë¡ˆ»Ø)
Student Number: 2015312911
*/

/* page 19 */
#include <stdio.h>

void main(void)
{
	printf("I love programming\n");
	printf("You will love it too once ");
	printf("you know the trick\n");
	getchar();

	system("pause");
}
/*Output:
I love programming
You will love it too once you know the trick
*/


/* page 25 */
#include <stdio.h>

void main(void)
{
	printf("Line : %d\n", __LINE__);
	printf("%s\n", __FILE__);
	printf("%s\n", __DATE__);
	printf("%s\n", __TIME__);
	printf("Line : %d\n\n", __LINE__);
	printf("ANSI : %d\n", __STDC_SECURE_LIB__);
	printf("ANSI : %d\n", __STDC_HOSTED__);
	getchar();
}
/* Ouput:
Line : 5
C:\Users\Jihwan\Desktop\EEEProgramming\main.c
Mar 28 2020
02:34:14
Line : 9

ANSI : 200411
ANSI : 1
*/




/*page 25*/
#include <stdio.h>
#define pi 3.141592

void main(void)
{
	double height, radius, base, volume;

	printf("Enter the height and radius of the cone: ");
	scanf_s("%lf %lf", &height, &radius);

	base = pi * radius * radius;
	volume = (1.0 / 3.0) * base * height;

	printf("\nThe volume of a cone is %f\n", volume);
	system("pause");
}
/*Output:
Enter the height and radius of the cone: 2 3

The volume of a cone is 18.849552
*/

/*page 53*/
#include <stdio.h>

void main(void)
{
	int int1, int2, int_sum;
	float float1, float2, float_sum;
	int1 = 17; int2 = 25; int_sum = int1 + int2;
	float1 = 3.5; float2 = 7.8; float_sum = float1 + float2;

	printf("int1 = %3d, int2 = 3d\n", int1, int2);
	printf("int1 + in2 %d\n\n", int_sum);
	printf("float1 = %3.2f, float2 = %3.2f\n", float1, float2);
	printf("float1 + float2 = %3.2f\n\n", float_sum);

	printf("int1 + float2 = %3.2f\n\n", int1 + float2);
	return 0;
}
/*Output:
int1 =  17, int2 =  25
int1 + int2 42

float1 = 3.50, float2 = 7.80
float1 + float2 = 11.30

int1 + float2 = 24.80
*/




