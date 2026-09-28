#define _CRT_SECURE_NO_WARNINGS
#include "ScheduleQueue.h"

void queueCreate(int_queue_t* queue)
{
  	queue->front = NULL;
  	queue->rear = NULL;
  	queue->nodeCount = 0;
}


int queueFront(int_queue_t* queue)
{
  	if (queue->front == NULL)
  		return -1;
  	return queue->front->data;
}


int queuePush(int_queue_t* queue, int input)
{
  	//if first element and last element in queue 
  	node_t* temp = malloc(sizeof(node_t));
  	temp->data = input;
  	temp->nextNode = NULL;

  	if (queue->front == NULL)
  		queue->front = temp;
  	else
  		queue->rear->nextNode = temp;
  	queue->rear = temp;

  	return ++queue->nodeCount;
}


int queuePop(int_queue_t* queue)
{
  	node_t* temp = queue->front;
  	int ret;

  	if (queue->front == NULL)
  		return -1;
  	queue->front = queue->front->nextNode;
  	if (queue->front == NULL)
  		queue->rear = NULL;
  	queue->nodeCount--;
  	ret = temp->data;
  	free(temp);
  	return ret;
}



int queueIsEmpty(const int_queue_t* queue)
{
	  return queue->nodeCount == 0;
}



void queueDisplay(int_queue_t* queue)
{
    char str[16];
    int i = 0;
   	node_t* tempNode = queue->front;
   	
   	memset(str, ' ', 16);
  	while (tempNode != NULL)
  	{
  	   if(i >= 15) break; 
  	   str[i++] = ( (tempNode->data) + '0');
  	   tempNode = tempNode->nextNode;
  	}
  	
  	write_string(0x00, str);
  	ms_delay(10);
}


int queueSize(const int_queue_t* queue)
{
	  return queue->nodeCount;
}


int queueIsFull(const int_queue_t* queue)
{
  	if (queue->front != NULL)
  		return 1;
  	else
  		return 0;
}






