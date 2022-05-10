#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <assert.h>

int main(int argc, char * argv[])
{
	int fd;
	char input[2]={0};
	unsigned char t =0;

	if (argc <= 1) {
		printf("please input the parameter! ex)./test 0 ~ 255\n");
		return -1;
	}

	fd = open("/dev/kjh_fpga7segment", O_WRONLY);
	if (fd != -1){
		t = atoi(argv[1]);
		printf("value : %d, %X \n", t, t);
		if (t > 255) {
			printf("please input the parameter! ex)./test 0 ~ 255\n");
			close(fd);
			return -1;
		}
		input[0] = t/16;
		input[1] = t%16;
	}
	else {
		printf("Device Open error!\n");
		return -1;
	}

	write(fd, input, 2);

	close(fd);
	return 0;
}
