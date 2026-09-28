#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

int main(void)
{
	int fd;
	int i;

	unsigned char nullValue = 0x00;
	unsigned char values[] = { 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x21};	// do, re, mi, ...

	fd = open("/dev/kjh_fpgaPiezo", O_WRONLY);
	assert(fd != 0);

	for (i = 0; i < 3; ++i)
	{
		write(fd, &values[i], 1);	// write(fd, values + i, 1);
		usleep(500000);
		write(fd, &nullValue, 1);
	}
	close(fd);
	return 0;
}
