/*
 * Converts distanes from miles to kilometers.
 */

#include <stdio.h>

#include <stdio.h> /* printf, scanf definitions */
#define KMS_PER_MILE 1.609 /* Conversion Constant  */

int main(void) 
{

    double miles, kms;

    /* Get the dsitance in miles. */
    printf("Enter the distance in miles");
    scanf("%lf", &miles);

    /* Convert the distance to kilmeters. */ 
    kms = KMS_PER_MILE * miles;

    /* Display the distance in kilometers. */
    printf("The equals %f kilometers. \n", kms);

    return 0;
}

