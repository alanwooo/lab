/*gcc -Wall -g list.c  -o list*/
# include <stdio.h>
# include <stdlib.h>
# include <stdbool.h> /*import boot: true, false*/

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


ListNode *LoopList() {
    ListNode *List = CreateList(0);
    for(int i = 20; i <= 40; i++) {
        AddNodeTail(List, i);
    }
    PrintList(List);
    ListNode *p, *head;
    head = List;
    while(head && head->val != 33) {
        head = head->next;
    }
    p = head;
    while(head->next){
        head = head->next;
    }
    head->next = p;
    return List;
}

bool CheckLoop(ListNode *head) {
    ListNode *fast, *low;
    fast = low = head;
    printf("Starting check\n");
    while(1) {
        fast = fast->next->next;
        low = low->next;
        if(fast == low) return true;
        if(!fast || !fast->next) return false;
    }
}

void FindCommonNode(ListNode *head) {
    ListNode *fast, *low, *p;
    p = fast = low = head;
    while(1) {
        fast = fast->next->next;
        low = low->next;
        if(fast == low) break;
    }
    int Length = 0;
    while(p != low) {
        Length++;
        p = p->next;
        low = low->next;
    }
    printf("Loop entry is %d, entry length %d\n", p->val, ++Length);
    int LoopLength = 0;
    ListNode *entry = p;
    while(entry != p->next) {
        LoopLength++;
        p = p->next;
    }
    printf("Loop length %d\n", ++LoopLength);
}

int LastNNode(ListNode *head, int n) {
    ListNode *q, *p;
    q = p = head;
    for(int i = 0; i < n; i++) {
        p = p->next;
    }
    while(p) {
        q = q->next;
        p = p->next;
    }
    return q->val;
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
    printf("Last %d val is %d\n", 4, LastNNode(List, 4));
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
    printf("loop %d\n", CheckLoop(List)?0:1);
    ListNode *Loop = LoopList();
    printf("loop %d\n", CheckLoop(Loop)?0:1);
    FindCommonNode(Loop);
    return 0;
}
