#pragma once

#include <vector>
#include <memory>
#include <iostream>


struct ListNode
{
    int val;
    std::shared_ptr<ListNode> next;
    ListNode(int val = 0):val{val}{}
};


auto make_list(const auto &v){
    if(v.empty()) return std::shared_ptr<ListNode>{};

    auto head = std::make_shared<ListNode>(v[0]);
    auto tail = head;

    for(auto i = 1; i < v.size(); i++) {
        auto tmp = tail;
        tail = std::make_shared<ListNode>(v[i]);
        tmp->next = tail;
    }

    return head;
}


void print_list(auto head) {
    auto i = 0;
    while (head && i < 100){
        std::cout << head->val;
        if(head->next) std::cout << "->";
        head = head->next;
        i++;
    }
    std::cout << std::endl;
}