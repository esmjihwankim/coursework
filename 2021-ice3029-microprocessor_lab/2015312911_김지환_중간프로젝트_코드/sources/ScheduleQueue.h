
#ifndef SCHEDULEQUEUE_H
#define SCHEDULEQUEUE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/*********************************************/
/* @brief Singly Linked List Based Queue ADT */
/*********************************************/



typedef struct node_t
{
	char* data;
	struct node_t* nextNode;
}node_t;


typedef struct strqueue_t
{
	node_t* front;
	node_t* rear; 
	int nodeCount;
}strqueue_t;

extern struct strqueue_t global_q;

void queueCreate(strqueue_t* queue);
char* queueFront(strqueue_t* queue);
int queuePush(strqueue_t* queue, const char* str);
char* queuePop(strqueue_t* queue);
int queueIsEmpty(const strqueue_t* queue);
int queueSize(const strqueue_t* queue);
int queueIsFull(const strqueue_t* queue);

// for debug on pc  
void queueDisplay(strqueue_t* queue);

#endif // !SCHEDULEQUEUE_H