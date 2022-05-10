#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

int main(void)
{
	int fd;
	if ((fd = open("/dev/kjh_fpgaled", O_WRONLY)) < 0){
		fprintf(stdout, "can't open the driver");
		return -1;
	}

	for (;;)// infinite loop
	{
		unsigned char ch;
		int value;
		fprintf(stdout, "Input LED value [0-255] : ");
		fscanf(stdin, "%d", &value);
		ch = (unsigned char) value;
		write(fd, &ch, 1);
	}
	close(fd);
	return 0;
}
