/*
Programmer : Jihwan Kim
Student Number : 2015312911

Purpose : To read from file and access, sort automatically calculate grade based on professor input 
There are separate portals for Professor and the student. 

The 'functions' and 'screens' are separated by multiple starred comment lines i.e. //*****

When the professor goes to the show all results screen, the program displays a sorted (descending order) data and is stored in that manner

Care must be taken in using this program that it is case sesitive when taking input from users. For example, M and m are regarded as different. 

Sorting based on student scores done by selection sort
*/

#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <Windows.h>

//Global Variables
char toBack = 'B';
char toExit = 'E';
char toMain = 'M';

//Functions 
void showOptions(void);
char takeInput(char c1[20], char c2[20]);
void upload(struct subject* subject, FILE* fp);
void printStudentList(struct subject* subject);
int inputScoreLimit(void);
void percentageGrade(struct subject* subject, int iaScoreLimit[4]);
void showResultForStudent(struct subject* subject, int index);
void sortInDescending(struct subject* subject);


//Screens
void welcomeScreen(void);
void mainScreen(struct subject* math, struct subject* science);
void professorScreen(struct subject* math, struct subject* science);
void showAllRecordsScreen(struct subject* math, struct subject* science);
void calculateFinalGradesScreen(struct subject* math, struct subject* science);
void studentScreen(struct subject* math, struct subject* science);


//Data structure to store necessary information
struct student {
	char id[20];
	char name[20];
	int midScore;
	int projectScore;
	int finalScore;
	int totalScore;
	double percentage;
	char grade;
};

struct subject {
	char courseName[50];
	char Instructor[50];
	struct student studentList[100];
	int studentCount;
};

int main(void) {
	welcomeScreen();
	system("pause");
	return 0;
}



//FUNCTIONS ****************************************************************
//**************************************************************************
//**************************************************************************
//**************************************************************************

//Prints default options valid throughout all screens 
void showOptions() {
	printf("********\nB for Back\nE for Exit\nM for Main\n********\n\n\n");
}

//Takes input from user in each screen. Commands are for moving between screens, writing to files, etc. c1 and c2 may vary depending on the screen
char takeInput(char c1[20], char c2[20]) { //string input is the parameter in case when user inputs multiple characters instead of a single one. 

	fflush(stdin);
	char strInput[20]; 
	//printf("#100 TakeInput\n");

	while (1) {
		//printf("#200 loop\n");
		scanf("%s", strInput);

		if (strcmp(strInput, "B") != 0
			&& strcmp(strInput, "E") != 0
			&& strcmp(strInput, "M") != 0
			&& strcmp(strInput, c1) != 0
			&& strcmp(strInput, c2) != 0) {

			printf("Wrong Command. Please Try again.\n");
			fflush(stdin);
			continue;
		}

		else {
			break;
		}
	}

	return strInput[0];
}

//Parse file into struct data type in the memory. The data comes in the following format
//ID	NAME 	MID	PROJECT	FINAL	TOTAL
void upload(struct subject* subject, FILE* fp) {
	char c, cTmp;
	char rubbish[20], tmpID[30], tmpName[30];
	char line[200];
	int i = 0, j = 0;

	subject->studentCount = 0;

	//skip the criteria line i.e) ID NAME MID ... 
	fscanf(fp, "%s %s %c %s", rubbish, rubbish, &cTmp, subject->courseName);
	fscanf(fp, "%s %c %s", rubbish, &cTmp, subject->Instructor);
	fscanf(fp, "%s %s %s %s %s %s", rubbish, rubbish, rubbish, rubbish, rubbish, rubbish);

	while (!feof(fp)) {
		fscanf(fp, "%s %s %d %d %d %d",
			subject->studentList[i].id,
			subject->studentList[i].name,
			&(subject->studentList[i].midScore),
			&(subject->studentList[i].projectScore),
			&(subject->studentList[i].finalScore),
			&(subject->studentList[i].totalScore)
		);
		//Initialize just in case
		subject->studentList[i].percentage = 0.00;
		subject->studentList[i].grade = '\0';
		//increment student count
		subject->studentCount++;
		i++;
	}
	subject->studentCount--;
	return;
}

//Takes structure and prints in console
void printStudentList(struct subject* subject) {
	int i;
	printf("Course name : %s\n", subject->courseName);
	printf("Instructor : %s\n", subject->Instructor);

	printf("\n%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s\n", 
		"ID", "NAME", "MID", "PROJECT", "FINAL", "TOTAL", "PERCENTAGE", "GRADE");

	for (i = (subject->studentCount) - 1; i >= 0; i--) {
		printf("%-12s%-12s%-12d%-12d%-12d%-12d%-12.3lf%-12c\n",
			subject->studentList[i].id,
			subject->studentList[i].name,
			subject->studentList[i].midScore, 
			subject->studentList[i].projectScore,
			subject->studentList[i].finalScore,
			subject->studentList[i].totalScore,
			subject->studentList[i].percentage,
			subject->studentList[i].grade
		);
	}

	printf("\n");
}

//Input the Score threshold for each Grade 
//i.e) A, B, C .. Unspecified score by user will automatically be F which I do not expect to get in this course 
int inputScoreLimit(void) {
	double dTmp;
	int iTmp;
	int validity; 

	while (1) {
		validity = scanf("%lf", &dTmp);

		if (validity != 1) {
			printf("Values other than INTEGER TYPE are NOT Allowed!\n");
			while (getchar() != '\n');
			continue;
		}

		//when value is floating point 
		if ((dTmp / 100) < 0.01) {
			printf("Decimal inputs are not allowed. Please enter a whole number\n");
			continue;
		}

		iTmp = (int)dTmp;
		//when value out or range
		if (iTmp > 100 && iTmp < 0) {
			printf("Invalid Input. Please try again.\n");
			continue;
		}

		//passed all tests, break
		break;
	}

	return iTmp;
}

//Calculates Percentage and Grade for each student 
void percentageGrade(struct subject* subject, int iaScoreLimit[4]) {
	int i;

	//calculate percentage and input grade
	for (i = 0; i < (subject->studentCount); i++) {
		//percentage
		subject->studentList[i].percentage = ((double)(subject->studentList[i].totalScore)) / 3;

		//grade - 'N' for grades Lower than D
		if ((subject->studentList[i].percentage > iaScoreLimit[0]))
			subject->studentList[i].grade = 'A';
		else if ((subject->studentList[i].percentage > iaScoreLimit[1]))
			subject->studentList[i].grade = 'B';
		else if ((subject->studentList[i].percentage > iaScoreLimit[2]))
			subject->studentList[i].grade = 'C';
		else if ((subject->studentList[i].percentage > iaScoreLimit[3]))
			subject->studentList[i].grade = 'D';
		else subject->studentList[i].grade = 'F';
	}

}

//Write the data inside structure into the file in a specified format 
void writeResults(struct subject* subject, FILE* fp) {
	int i;

	fprintf(fp,"Course name : %s\n", subject->courseName);
	fprintf(fp, "Instructor : %s\n", subject->Instructor);

	fprintf(fp, "\n%-9s%-9s%-9s%-9s%-9s%-9s%-9s%-9s\n",
		"ID", "NAME", "MID", "PROJECT", "FINAL", "TOTAL", "PERCENT", "GRADE");

	for (i = (subject->studentCount) - 1; i >= 0; i--) {
		fprintf(fp, "%-9s%-9s%-9d%-9d%-9d%-9d%-9.3lf%-9c\n",
			subject->studentList[i].id, 
			subject->studentList[i].name,
			subject->studentList[i].midScore, 
			subject->studentList[i].projectScore,
			subject->studentList[i].finalScore, 
			subject->studentList[i].totalScore,
			subject->studentList[i].percentage,
			subject->studentList[i].grade 
		);
	}

	fprintf(fp, "\n\n");
}

//Prints results for students ::: Called from Student Screen
void showResultForStudent(struct subject* subject, int index) {
	printf("Course name : %s\n", subject->courseName);
	printf("Instructor : %s\n", subject->Instructor);

	printf("\n%-12s%-12s%-12s%-12s%-12s%-12s%-12s%-12s\n",
		"ID", "NAME", "MID", "PROJECT", "FINAL", "TOTAL", "PERCENTAGE", "GRADE");

	printf("%-12s%-12s%-12d%-12d%-12d%-12d%-12.3lf%-12c\n",
		subject->studentList[index].id,
		subject->studentList[index].name,
		subject->studentList[index].midScore, 
		subject->studentList[index].projectScore,
		subject->studentList[index].finalScore, 
		subject->studentList[index].totalScore,
		subject->studentList[index].percentage, 
		subject->studentList[index].grade
	);

	printf("\n");
}

//Sorts the student result in descenting order - sorting based on total score
void sortInDescending(struct subject* subject) {
	int i, j;
	int iCount = subject->studentCount;
	struct subject tmp;

	//based on selection sort 
	//i == j - 1
	for (i = 0; i < iCount - 1 ; i++) {
		for (j = i + 1; j < iCount; j++) {

			if (subject->studentList[i].totalScore > subject->studentList[j].totalScore) {
				tmp.studentList[0] = subject->studentList[j];
				subject->studentList[j] = subject->studentList[i];
				subject->studentList[i] = tmp.studentList[0];
			}
		}
	}


}


//SCREENS*******************************************************************
//**************************************************************************
//**************************************************************************
//**************************************************************************

//welcome screen
void welcomeScreen(void) {
	char firstFileName[30], secondFileName[30];
	int i, j;
	char c;
	FILE* fp1 = NULL;
	FILE* fp2 = NULL;

	struct subject sMath, * spMath = &sMath;
	struct subject sScience, * spScience = &sScience;

	//Starting off with a welcome screen
	//Upload file into the system : 
	//1. First file uploaded into the system, file closed
	//2. Second file uploaded into the system, file closed 
	printf("--WELCOME--\nEnter the First file name\n");

	while (1) {
		scanf("%s", firstFileName);
		fp1 = fopen(firstFileName, "r");
		if (fp1 == NULL) {
			printf("The file isn't uploaded, try again\n");
		}
		else break;
	}
	upload(spMath, fp1);
	fclose(fp1);

	printf("Enter the Second File Name\n");
	while (1) {
		scanf("%s", secondFileName);
		fp2 = fopen(secondFileName, "r");
		if (fp2 == NULL) {
			printf("The file isn't uploaded, try again\n");
		}
		else break;
	}
	upload(spScience, fp2);
	fclose(fp2);
	system("cls");
	//End of Welcome Screen. Move to Main Screen

	mainScreen(spMath, spScience);
}

//main screen for login
void mainScreen(struct subject* spMath, struct subject* spScience) {
	char cInput, tmp;
	showOptions();
	printf("--MAIN--\nPlease Press\n\nP for Professor\nS for Student\n\n");
	
	//take user input and reject invalid input 
	//main screen takes 'p' and 's' 
	cInput = takeInput("P", "S");

	//moving to another screen
	//case for moving back to welcome screen - 'b' 
	if (cInput == toBack) {
		system("cls");
		welcomeScreen();
	}
	else if (cInput == toExit) {
		return;
	}
	else if (cInput == toMain) {
		printf("Already in Main Screen\n");
		mainScreen(spMath, spScience);
	}
	//To Professor Portal
	else if (cInput == 'P') {
		system("cls");
		professorScreen(spMath, spScience);
	}
	//To Student Portal
	else if (cInput == 'S') {
		system("cls");
		studentScreen(spMath, spScience);
	}

	return;
}

//professor screen : can move to 1. Show all Records, 2. Calculate Final Grades
void professorScreen(struct subject* spMath, struct subject* spScience) {
	char cInput;
	
	showOptions();
	printf("--Professor Portal--\n\nPlease Press\nS for Show All Records\nC for Calculate the Final Grades\n");

	//take user input and reject invalid input
	//professor screen takes 's' and 'c'
	cInput = takeInput("S", "C");

	//back
	if (cInput == toBack) {
		system("cls");
		mainScreen(spMath, spScience);
	}
	//exit 
	else if (cInput == toExit) {
		return;
	}
	//main
	else if (cInput == toMain) {
		system("cls");
		mainScreen(spMath, spScience);
	}

	else if (cInput == 'S') {
		system("cls");
		showAllRecordsScreen(spMath, spScience);
	}

	else if (cInput == 'C') {
		system("cls");
		calculateFinalGradesScreen(spMath, spScience);
	}

}

void showAllRecordsScreen(struct subject *spMath, struct subject *spScience) {

	sortInDescending(spMath);
	sortInDescending(spScience);

	int iInput;
	printf("--showAllRecords--\n");

	//show record 
	printStudentList(spMath);
	printStudentList(spScience);

	showOptions();
	iInput = takeInput(toBack, toMain);
	
	//possible move from here : Back, Exit, Main
	if (iInput == toBack) {
		system("cls");
		professorScreen(spMath, spScience);
	}
	if (iInput == toExit) {
		return;
	}
	if (iInput == toMain) {
		system("cls");
		mainScreen(spMath, spScience);
	}
	return;
}

void calculateFinalGradesScreen(struct subject *spMath, struct subject *spScience) {
	char cInput;
	int iTmp, i;
	int iaScoreLimit[4];
	
	showOptions();
	printf("--Calculate Final Grades--\n");
	printf("IMPORTANT : Please enter only integer values and also enter the MIN Value of each Grade\n");
	printf("e.g) Only those students will get grade 'A' whose percentage is greater than 90 percent,\n");
	printf("the enter 90 for grade A Default Grading Policy\n");

	//Takes a score limit value for a particular grade -rejects float, character, string
	//Also needs to reject value when input for lower percentage is greater than the previous one
	printf("Please enter Percentage for Grade A\n");
	iTmp = inputScoreLimit();
	iaScoreLimit[0] = iTmp;

	for (i = 1; i <= 3; i++) {

		while (1) {
			printf("Please enter Percentage for Grade %c\n", ('A' + i));
			iTmp = inputScoreLimit();
			if (iaScoreLimit[i - 1] < iTmp || iaScoreLimit[i - 1] == iTmp) {
				printf("Score for %c must be less than %c\n", ('A' + i), ('A' + i - 1));
				continue;
			}
			else {
				iaScoreLimit[i] = iTmp;
				break;
			}
		}

	} //Entering score for grades completed

	//Calculate percentage and grade 
	percentageGrade(spMath, iaScoreLimit);
	percentageGrade(spScience, iaScoreLimit);

	//Print
	printStudentList(spMath);
	printStudentList(spScience);

	//Take Input
	printf("Do you want to write the grades in another file?\nPlease Press\n");
	printf("Y for Yes\nN for No\n");
	cInput = takeInput("Y", "N");

	if (cInput == toBack) {
		system("cls");
		professorScreen(spMath, spScience);
	}
	else if (cInput == toExit) return;
	else if (cInput == toMain) {
		system("cls");
		mainScreen(spMath, spScience);
	}
	else if (cInput == 'N') {
		system("cls");
		mainScreen(spMath, spScience);
	}
	else if (cInput == 'Y') { //Write

		FILE* fp;
		fp = fopen("result.txt", "w");
		writeResults(spMath, fp);
		writeResults(spScience, fp);
		fclose(fp);
		printf("Write completed. Thank you.\n");

		//takes input for Back Exit Main 
		showOptions();
		cInput = takeInput("B", "E");
		
		if (cInput == toBack) {
			system("cls");
			professorScreen(spMath, spScience);
		}

		else if (cInput == toExit) {
			system("cls");
			return;
		}
		else if (cInput == toMain) {
			system("cls");
			mainScreen(spMath, spScience);
		}
	}
}

//Student Portal
void studentScreen(struct subject* spMath, struct subject* spScience) {
	int i, validity, foundFlag = 0;
	char cInput;
	char strInput[10];

	while (1) {
		//Take input
		printf("Please enter your ID or Name in order to check your scores\n");
		validity = scanf("%s", strInput);

		//compare with data inside structures
		for (i = 0; i < spMath->studentCount; i++) {
			//Check for math
			if (strcmp(spMath->studentList[i].name, strInput) == 0 || strcmp(spMath->studentList[i].id, strInput) == 0) {
				foundFlag = 1;
				showResultForStudent(spMath, i);
			}

			//Check for science
			if (strcmp(spScience->studentList[i].name, strInput) == 0 || strcmp(spScience->studentList[i].id, strInput) == 0) {
				foundFlag = 1;
				showResultForStudent(spScience, i);
			}
		}
		break;
	}

	if (foundFlag == 0) {
		printf("There were no matching names\n");
	}

	showOptions();
	cInput = takeInput("B","E");
	if (cInput == toBack) {
		system("cls");
		mainScreen(spMath,spScience);
	}
	else if (cInput == toExit) {
		return;
	}
	else if (cInput == toMain) {
		system("cls");
		mainScreen(spMath, spScience);
	}
}












