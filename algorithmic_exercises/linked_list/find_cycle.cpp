#include "linked_list.hpp"
#include <assert.h>

using namespace std;


bool is_cycled(auto head) {
    auto fast = head;
    auto slow = head;


    while(fast && fast->next){
        fast = fast->next->next;
        slow = slow->next;
        if(slow == fast) return true;
    }
    return false;
}


auto cycle_start_position(auto head) {
    auto fast = head;
    auto slow = head;

    while(fast && fast->next){
        fast = fast->next->next;
        slow = slow->next;
        if(slow == fast){
            fast = head;
            while(slow != fast) {
                slow = slow->next;
                fast = fast->next;
            }

            return fast;
        }
    }

    return decltype(head){};
}


void break_cycle(auto head) {
    auto cycle_start = cycle_start_position(head);

    if(!cycle_start) return;
    auto p = cycle_start;
    while(p->next != cycle_start) p = p->next;
    p->next.reset();
}





int main()
{

    auto head = make_list(vector{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20});

    print_list(head);

    assert(is_cycled(head) == false);
    assert(!cycle_start_position(head));


    // add cycle with start in 10
    auto p = head;
    auto cycle_start = p;
    while(p->next) {
        if(p->val == 10) cycle_start = p;
        p = p->next;
    }
    p->next = cycle_start;

    assert(is_cycled(head) == true);
    assert(cycle_start == cycle_start_position(head));


    break_cycle(head);
    assert(!cycle_start_position(head));

    return 0;
}