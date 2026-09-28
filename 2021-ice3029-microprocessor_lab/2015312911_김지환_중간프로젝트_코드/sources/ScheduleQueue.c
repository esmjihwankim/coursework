
#define _CRT_SECURE_NO_WARNINGS
#include "ScheduleQueue.h"

struct strqueue_t global_q;

void queueCreate(strqueue_t* queue)
{
	queue->front = NULL;
	queue->rear = NULL;
	queue->nodeCount = 0;
}


char* queueFront(strqueue_t* queue)
{
	if (queue->front == NULL)
		return NULL;
	return queue->front->data;
}


int queuePush(strqueue_t* queue, const char* str)
{
	//if first element and last element in queue 
	node_t* temp = malloc(sizeof(node_t));
	temp->data = malloc(strlen(str) + 1);
	strcpy(temp->data, str);
	temp->nextNode = NULL;
	
	if (queue->front == NULL)
		queue->front = temp;
	else
		queue->rear->nextNode = temp;
	queue->rear = temp;

	return ++queue->nodeCount;
}

char* queuePop(strqueue_t* queue)
{
	node_t* temp = queue->front;
	char* ret = NULL;

	if (queue->front == NULL)
		return NULL;
	queue->front = queue->front->nextNode;
	if (queue->front == NULL)
		queue->rear = NULL;
	queue->nodeCount--;
	ret = temp->data;
	free(temp);
	return ret;
}



int queueIsEmpty(const strqueue_t* queue)
{
	return queue->nodeCount == 0;
}



void queueDisplay(strqueue_t* queue)
{
	node_t* tempNode = queue->front;
	while (tempNode != NULL)
	{
		printf("%s\n", tempNode->data);
		tempNode = tempNode->nextNode;
	}
}


int queueSize(const strqueue_t* queue)
{
	return queue->nodeCount;
}


int queueIsFull(const strqueue_t* queue)
{
	if (queue->front != NULL)
		return 1;
	else
		return 0;
}



