/*gcc -Wall -g list.c  -o list*/
# include <stdio.h>
# include <stdlib.h>

typedef struct ListNode {
    struct ListNode *next;
    int val;
} ListNode;

ListNode *CreateList(int val) {
    ListNode *List = (ListNode *)malloc(sizeof(ListNode));
    if (!List) return NULL;
    List->next = NULL;
    List->val = 0;
    return List;
}

void PrintList(ListNode *head) {
    ListNode *n = head;
    while (n) {
        printf("->%d", n->val);
        n = n->next;
    }
    printf("\n");
}

ListNode *AddNodeTail(ListNode *head, int val) {
    if(!head) return NULL;
    ListNode *n = head;
    while(n->next) {
        n = n->next;
    }
    ListNode *m = (ListNode *)malloc(sizeof(ListNode));
    m->next = NULL;
    m->val = val;
    n->next = m;
    return head;
}

ListNode *AddNodeHead(ListNode *head, int val) {
    if(!head) return NULL;
    ListNode *n = (ListNode *)malloc(sizeof(ListNode));
    n->val = val;
    n->next = head;
    return n;
}

ListNode *DeleteNode(ListNode *head, int val) {
    if(!head) return NULL;
    ListNode *p, *n;
    n = head;
    while(n->val != val) {
        p = n;
        n = n->next;
        if(!n) {
            printf("Warning: Did not find the node %d.\n", val);
            return head;
        }
    }
    /*if it is head node*/
    if(n == head) {
        if(n->next) {
            printf("Delete head.\n");
            head = n->next;
        } else {
            printf("Delete head, list is none.\n");
            head = NULL;
        }
    } else {
        p->next = n->next;
    }
    free(n);
    return head;
}

ListNode *InsertNode(ListNode *head, int val, int pos) {
    if(!head) return NULL;
    int i = 1;
    ListNode *n = head;
    while(i != pos) {
        if(!n->next) {
            printf("Length is %d, postion is %d.\n", i, pos);
            break;
        }
        n = n->next;
        i++;
    }
    ListNode *p = (ListNode *)malloc(sizeof(ListNode));
    p->val = val;
    p->next = n->next;
    n->next = p;
    return head;
}

ListNode *Revert(ListNode *head) {
    if(!head) return NULL;
    /* NULL<-o<-o<-p<-n q->o->o->NULL*/
    ListNode *n, *p, *q;
    n = p = q = head;
    while(n->next) {
        q = n->next;
        if(n == head) {
            p->next = NULL;
        } else {
            n->next = p;
        }
        p = n;
        n = q;
    }
    n->next = p;
    return n;
}

int main() {
    int i = 1, j = 1;
    printf("i++ = %d, i = %d, ++j = %d, j = %d\n", i++, i, ++j, j);
    ListNode *List = CreateList(0);
    /*PrintList(List);
    List = DeleteNode(List, 0);*/
    if(!List) return 1;
    for(int i = 1; i <= 10; i++) { 
        AddNodeTail(List, i);
    }
    PrintList(List);
    List = DeleteNode(List, 5);
    PrintList(List);
    List = DeleteNode(List, 0);
    PrintList(List);
    List = DeleteNode(List, 10);
    PrintList(List);
    List = DeleteNode(List, 200);
    PrintList(List);
    for(int i = 1; i < 10; i++) {
        List = AddNodeHead(List, i);
    }
    PrintList(List);
    InsertNode(List, 100, 1);
    PrintList(List);
    InsertNode(List, 111, 111);
    PrintList(List);
    InsertNode(List, 110, 5);
    PrintList(List);
    List = Revert(List);
    PrintList(List);
    return 0;
}
