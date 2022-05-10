#ifndef SCHEDULEQUEUE_H
#define SCHEDULEQUEUE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lcd.h"


/*********************************************/
/* @brief Singly Linked List Based Queue ADT */
/*********************************************/

typedef struct node
{
	int data;
	struct node* nextNode;
}node_t;


typedef struct int_queue
{
	node_t* front;
	node_t* rear;
	int nodeCount;
}int_queue_t;

extern struct int_queue g_queue;
extern struct int_queue g_history_queue;

void queueCreate(int_queue_t* queue);
int queueFront(int_queue_t* queue);
int queuePush(int_queue_t* queue, int input);
int queuePop(int_queue_t* queue);
int queueIsEmpty(const int_queue_t* queue);
int queueSize(const int_queue_t* queue);
int queueIsFull(const int_queue_t* queue);

// for debug on pc  
void queueDisplay(int_queue_t* queue);

#endif // !SCHEDULEQUEUE_H