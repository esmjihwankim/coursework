/*
Programmer : Jihwan Kim (±Ë¡ˆ»Ø)
Student Number : 2015312911

The purpose of this program is to implement various non-linear functions 
that can partially replace <Math.h> using Taylor(MacLaurin) Series Expansion.
The program will at first ask the user to choose between the provided function, 
then to enter input to be calculated.

Error Conditions exist for some functions. For example, Taylor Series for ln(x) will
only be valid in the range of positive real x. 
Hence, checking for error conditions for each function is prerequisite. 

The very first letters of most variables in this program represent specific data type.
For instance, dValue means double data type variable named Value.

Many of the functions that could have been put together in one function have been
separated to enhance readability. Having more parameters for a function that has multiple functionalities
made the readability suffer in an almost 700 line code.

The Functions are Mathemetically defined as follows
[1] cos(x)				Range : All Real x 
[2] sin(x)				Range : All Real x 
[3] tan(x)				Range : {x | x != PI/2 + k*PI, k = -1, 0, 1 .... }
[4] acos(x)				Range : 0<= x <= 1
[5] asin(x)				Range : 0 <= x <= 1
[6] atan[x]				Range : all real x 
[7] x^y					Range :	{x	 | All real x} {y | All real y}
[8] x^(1/y)			Range :	{x | x > 0} {y | all real y} To avoid imaginary numbers 
[9] e^x					Range : All Real x
[10]ln(x)				Range : x > 0
*/

#include <stdio.h>
#define PI 3.1415926535897
#define ITERATIONS 50
/*----------------------------- Function Declarations -----------------------------*/
void printLine(void);

void startOperation(int iCalculationType);
int askCalculationType(void);

int inputInteger(void);
double inputDouble(void);

void processTrig(int type, double originalInput, double radianInput);
void processInverseTrig(int type, double ratio);
void processPower(int type, double base, int exponent);
void processNatural(int type, double x);

int askAngleType(void);
double askAngleValue(void);
double toRadian(int type, double angle);
void printAngles(double angle);

double power(double x, int y);
double factorial(int x);

double taylorCos(double x);
double taylorSin(double x);
double taylorAcos(double x);
double taylorAsin(double x);
double taylorAtan(double x);

double taylorPower(int type, double x, int y);

double taylorExponential(double x);
double taylorNaturalLog(double x);


/*--------------------------------------------------- Main Function -------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------*/

void main(void) {
	int iCalculationType;

	while (1) {
		//Ask for user to choose the function 
		iCalculationType = askCalculationType();

		if (iCalculationType == -1) {
			break;
		}

		startOperation(iCalculationType);
		printf("\n\n#############################CALCULATION FINISHED##########################\n\n\n");
	}

	system("pause");
}


/*---------------------------------------- Non MATH related External Functions --------------------------------------
--------------------------------------------------------------------------------------------------------------------------------*/
// Prints dashed line for easy read 
void printLine(void) {
	int i;

	for (i = 0; i < 70; i++) {
		printf("-");
	}

	printf("\n");
}

//Takes integer value from user input and chekcs validity for general cases, for example, for alphabets and float values
int inputInteger(void) {

	double dInputValue;
	int validity;

	while (1) {
		//Will first take a double input to check if the input is a floating value by subtraction
		validity = scanf_s("%lf", &dInputValue);

		//Check for Alphabet
		if (validity != 1) {
			printf("Values other than INTEGER TYPE are not allowed. Try Again\n\n");
			while ((getchar()) != '\n');
			continue;
		}

		//Check for float
		else if (dInputValue - (int)dInputValue > 0) {
			printf("Floating point numbers are not allowed. Try Again\n\n");
			while ((getchar()) != '\n');
			continue;
		}
		else break;
	}

	return (int)dInputValue;
}

//Takes a double value from user input and validates it
double inputDouble(void) {

	double dInputValue;
	int validity;

	while (1) {
		validity = scanf_s("%lf", &dInputValue);

		if (validity != 1) {
			printf("Values other than DOUBLE TYPE are not allowed. Try Again\n\n");
			while ((getchar()) != '\n');
			continue;
		}

		else break;
	}

	return dInputValue;
}


//Received values based on their types
void startOperation(int iCalculationType) {
	int iAngleType;
	double dOriginalAngle, dRadAngle;
	double dBase; int iExponent;
	double dRatio, dValue;

	printf("\n\n");

	//Trig Operation
	if (iCalculationType <= 3) {
		iAngleType = askAngleType();
		dOriginalAngle = askAngleValue();
		dRadAngle = toRadian(iAngleType, dOriginalAngle);
		processTrig(iCalculationType,  dOriginalAngle, dRadAngle);
	}

	//Inverse Trig Operation
	else if (iCalculationType <= 6) {
		
		while (1) {
			// For arccos and arcsin, the range is -1<=0<=1
			// ArcTan can take any real value
			printf("Enter Ratio To Be Entered to The Inverse Trig Function\n");
			dRatio = inputDouble();

			if (iCalculationType <= 5) { //arcsin and arccos
				if ((dRatio < -1) || (dRatio > 1)) {
					printf("Error ::: You must enter number between -1 and 1\n");
					continue;
				}
				else break;
			} 
			break;
		}

		processInverseTrig(iCalculationType, dRatio);
	}

	//Power Functions
	else if (iCalculationType <= 8) {
		
		while (1) {

			printf("Enter Base\n");
			dBase = inputDouble();
			printf("Enter Exponent\n");
			iExponent = inputInteger();

			if (iCalculationType == 7) {
				break;
			}

			else {
				// x ^ (1/y)
				//Reject negative base values
				if (dBase < 0) {
					printf("Must Enter Base Value greater than 0. Try Again.\n");
					continue;
				}
				else break;
			}
		}

		processPower(iCalculationType, dBase, iExponent);
	}

	//Exponential and Natural Log
	else {
		while (1) {
			printf("Enter x\n");
			dValue = inputDouble();

			if (iCalculationType == 9) break; //exponential
			else { //natural log
				if (dValue <= 0) {
					printf("Error ::: Enter a value greater than 0\n");
					continue;
				}
				else {
					break;
				}
			}
		}

		processNatural(iCalculationType, dValue);
	}
}


// Ask user for required calculation
int askCalculationType(void) {
	int iInput;

	while (1) {
		printf("Input your desired Function. Enter -1 to Terminate.\n");
		printf("1) Cos(x)\n2) Sin(x)\n3) Tan(x)\n4) Acos(x)\n5) Asin(x)\n6) Atan(x)\n7) x^y\n8) x^(1/y)\n9) e^x\n10) loge(x)\n\n");
		iInput = inputInteger();
		printLine();

		iInput = iInput / 1;

		//Checks input out of range
		if (iInput == -1) {
			break;
		}

		else if (iInput >= 1 && iInput <= 10) {
			break;
		}

		else printf("Value out of range. Try Again.\n\n");

	}

	return iInput;
}

//Checks if the Input angle is in [Degree], [Radian] or [Gradian]
int askAngleType(void) {
	int iAngleType;
	

	while (1) {
		printf("Input Your Desired Angle Type\n1) Degrees\n2) Radians\n3) Gradians\n\n");
		iAngleType = inputInteger();

		if (iAngleType >= 1 && iAngleType <= 3) {
			break;
		}
		else {
			printf("Error:::Angle Type should be 1, 2, or 3\n");
			continue;
		}
	}
	
	printLine();
	return iAngleType;
}

//Ask for Desired Angle Value
double askAngleValue(void) {
	double dAngleValue;

	//For calculations that require angle values
	printf("\nInput the desired Angle Value\n");
	dAngleValue = inputDouble();
	
	printLine();
	return dAngleValue;
}

//Trigonometric Functions
void processTrig(int iCalculationType, double dOriginalAngle, double dRadAngle) {
	double dResult;

	//Calculations that require Taylor Expansion 
		switch (iCalculationType) {

		case 1: // cos(x)
			dResult = taylorCos(dRadAngle);
			printf("\nCos(%.2lf) = %f", dOriginalAngle, dResult);
			break;

		case 2: // sin(x)
			dResult = taylorSin(dRadAngle);
			printf("\nSin(%.2lf) = %f", dOriginalAngle, dResult);
			break;

		case 3: //tan(x)
			double dSinValue = taylorSin(dRadAngle);
			double dCosValue = taylorCos(dRadAngle);

			printf("\nTan(%.2lf) = ", dOriginalAngle);

			//Check Cosine value and determine output
			//Tan(90 degree) = Infinity 
			//Check if sqrt(cos^2(x)) is close to 0
			if (dCosValue * dCosValue < 0.000001) {
				printf("INFINITE ::: UNABLE TO GET A SPECIFIC VALUE");
			}
			else {
				dResult = taylorSin(dRadAngle) / taylorCos(dRadAngle);
				printf("%lf", dResult);
			}

			break;

		default:
			break;
		}
}


//Inverse Trigonometric Functions
void processInverseTrig(int type, double dRatio) {
	double dResultAngle;

	switch (type) {

	case 4: //acos(x)
		dResultAngle = taylorAcos(dRatio);
		printf("Acos(%.3lf)", dRatio);
		printAngles(dResultAngle);
		break;

	case 5: //asin(x)
		dResultAngle = taylorAsin(dRatio);
		printf("Asin(%.3lf)", dRatio);
		printAngles(dResultAngle);
		break;

	case 6: //atan(x)
		dResultAngle = taylorAtan(dRatio);
		printf("arctan(%.3lf)", dRatio);
		printAngles(dResultAngle);
		break;

	default:
		break;
	}
}


//Power Functions
void processPower(int type, double base, int exponent) {
	double dResult;

	switch (type)
	{
	case 7: //x^y
		dResult = taylorPower(type, base, exponent);
		printf("\n\n%lf ^ %d = %lf\n", base, exponent, dResult);
		break;

	case 8: //x^(1/y)
		dResult = taylorPower(type, base, exponent);
		printf("\n\n%lf ^ (1/%d) = %lf\n", base, exponent, dResult);
		break;

	default:
		break;
	}
}

//Exponential and Logarithmic Functions
void processNatural(int type, double x) {
	double dResult;
	
	switch (type)
	{
	case 9: //e^x
		dResult = taylorExponential(x);
		printf("e^(%lf) = %lf\n", x, dResult);
		break;

	case 10: //log e (x) or ln(x)
		dResult = taylorNaturalLog(x);
		printf("loge(%lf) = %lf\n", x, dResult);
		break;

	default:
		break;
	}
}


/*--------------------- Basic Mathematical Operations and Building Blocks of Taylor Series ---------------------
--------------------------------------------------------------------------------------------------------------------------------*/
//Converts other degree types to radian
double toRadian(int type, double angle) {

	double dRadianValue;
	switch (type)
	{
	case 1: //Input in Degrees
		dRadianValue = angle * (PI / 180);
		break;

	case 2: //Input in Radians 
		dRadianValue = angle;
		break;

	case 3: //Input in Gradians ::: 1 gradian = 
		dRadianValue = angle * (PI / 200);
		break;

	default:
		break;
	}

	return dRadianValue;
}

void printAngles(double radian) {
	double degreeValue, gradianValue;

	degreeValue = radian * (180.0 / PI);
	gradianValue = radian * (200.0 / PI);

	printf(" = %lf[Rad] = %lf[Degree] = %lf[Grad]\n\n", radian, degreeValue, gradianValue);
}


double power(double x, int y) {
	int i;
	double dPowResult = 1.0;

	for (i = 0; i < y; i++) {
		dPowResult = dPowResult * x;
	}

	return dPowResult;
}

//Calculates Factorial 
double factorial(int x) {
	int i;
	double dFactResult = 1.0;

	if (x < 0) {
		printf("Invalid Factorial\n");
		return 1.0;
	}
	else if (x == 0) {
		return 1;
	}

	for (i = x; i > 0; i--) {
		dFactResult = dFactResult * i;
	}

	return dFactResult;
}


/*----------------------------------------- Taylor Polynomial Realizations ----------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------*/ 
// cos(x)
double taylorCos(double x) {
	int n;
	double dOutput = 0.0;

	for (n = 0; n < ITERATIONS; n++) {

		double sign = power(-1, n);
		double xPowerY = power(x, 2*n);
		double TwoNFact = factorial(2 * n);

		dOutput = dOutput + sign * xPowerY * (1 / TwoNFact);
	}

	return dOutput;
}

//sin x
double taylorSin(double x) {
	int n;
	double dOutput = 0.0;
	double sign, xPowerY, twoNPlusFact;

	for (n = 0; n < ITERATIONS; n++) {

		sign = power(-1, n);
		xPowerY = power(x, 2 * n + 1);
		twoNPlusFact = factorial(2 * n + 1);
		dOutput = dOutput + sign * xPowerY * (1 / twoNPlusFact);
	}

	return dOutput;
}

//arcsin(x) = sum ( (2n)! * (1 / 4)
double taylorAsin(double x) {
	int n; 
	double dOuput = 0.0;
	double dTwoNFac, dFourPowerN, dNFacSquared, dTwoNPlusOne, dXPower;
	
	for (n = 0; n < ITERATIONS; n++){

		dTwoNFac = factorial(2 * n);
		dFourPowerN = power(4, n);
		dNFacSquared = power(factorial(n), 2);
		dTwoNPlusOne = 2 * n + 1;
		dXPower = power(x, 2 * n + 1);
		
		dOuput = dOuput + (dTwoNFac * (1.0 / dFourPowerN) * (1.0 / dNFacSquared) * (1.0 / dTwoNPlusOne) * dXPower);
	}

	return dOuput;
}

//arccos(x)
double taylorAcos(double x) {
	double dOutput;
	dOutput = (PI / 2) - taylorAsin(x);
	
	return dOutput;
}

//arctan(x)
double taylorAtan(double x) {
	//3 cases exist for computing arcTan(x)
	//1) x < -1 , 2) -1<= x <= 1 3) x > 1

	int n;
	double dOutput = 0.0;
	double dSum = 0.0;
	double sign, dTwoNPlus, dXPowerTwoN;

	//Calculate the summation value
	for (n = 0; n < ITERATIONS; n++) {
		sign = power(-1, n);
		dTwoNPlus = 2 * n + 1;
		dXPowerTwoN = power(x, 2 * n + 1);
		
		if ((-1 <= x) && (1 >= x)) {
			dSum = dSum + (sign * (1 / dTwoNPlus) * dXPowerTwoN);
		}
		else {
			dSum = dSum + (sign * (1 / dTwoNPlus) * (1 / dXPowerTwoN));
		}
	}

	//Consider the 3 cases depending on the value of x
	if (x < -1) {
		dOutput = (-PI / 2) - dSum;
	}

	else if ((-1 <= x) && (1 >= x)) {
		//Pass
		dOutput = dSum;
	}

	else { //x > 1
		dOutput = (PI / 2) - dSum;
	}

	return dOutput;
}


//x^y = e^(y* ln(x) )
//x^(1/y) = e^(1/y * ln(x)) 
double taylorPower(int iType, double x, int y) {
	double dExponentNaturalLog = 0.0;
	double dOutput = 0.0;
	double tempX = x;

	int tempY = y;
	if (y < 0) tempY *= -1;

	if (iType == 7) { // x ^ y
		if (x < 0) tempX *= -1;
		dExponentNaturalLog = taylorNaturalLog(tempX);
		dExponentNaturalLog *= tempY;
	}
	else { // x  ^ (1/y)
		dExponentNaturalLog = taylorNaturalLog(x);
		dExponentNaturalLog *= (1.0 / (double)tempY);
	}

	//calculate e^(exponentNaturalLog)
	dOutput = taylorExponential(dExponentNaturalLog);

	//CASES To CONSIDER ::  
	//When base is negative and exponent is an odd number 
	//negative exponent
	if (y < 0)  dOutput = 1.0 / dOutput;

	if (x < 0 && (tempY % 2 > 0)) { // Base negative and odd power will result in negative value 
		dOutput *= -1;
	}

	return dOutput;
}


//e^x
double taylorExponential(double x) {
	int n;
	double dSum = 0.0;
	double dOutput;
	double dXPower, fNFac;
	double tempX = x;

	if (x < 0) {
		tempX *= -1;
	}

	for (n = 0; n < ITERATIONS; n++) {
		dXPower = power(tempX, n);
		fNFac = factorial(n);

		dSum = dSum + dXPower * (1.0 / fNFac);
	}

	if (x < 0) {
		dOutput = 1.0 / (dSum);
	}
	else {
		dOutput = dSum;
	}

	return dOutput;
}

// log e (x) or ln(x)
double taylorNaturalLog(double x) {
	int n;
	double dOutput = 0.0;
	double xMinusPlus = (x - 1) / (x + 1);
	double xPower2N;

	//ln(x) = 2 * sum 1->inf((x - 1) / (x + 1)) ^ (2n - 1) / (2n - 1)
	for (n = 1; n <= ITERATIONS; n++) {
		xPower2N = power(xMinusPlus, 2 * n - 1);
		dOutput = dOutput + (xPower2N / (2 * n - 1));
	}
	dOutput = dOutput * 2;

	return dOutput;
}






