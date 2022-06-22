#pragma once

#include <memory>
#include <algorithm>
#include <vector>
#include <cmath>
#include <functional>
#include <iostream>
#include <stack>

struct Node {
    int val;
    std::shared_ptr<Node> left;
    std::shared_ptr<Node> right;
    std::weak_ptr<Node> parent;
    int * node;

    size_t child_count = {0};
    Node(int val = 0):val{val} {}
};


auto make_tree(auto const& v, size_t i = 0){

    if(v.empty() || i >= v.size()) return std::shared_ptr<Node>{};

    auto root = std::make_shared<Node>(v[i]);
    root->left = make_tree(v, 2 * i + 1);
    root->right = make_tree(v, 2 * i + 2);

    if(root->left) {
        root->child_count += root->left->child_count + 1;
        root->left->parent = root;
    }

    if(root->right) {
        root->child_count += root->right->child_count + 1;
        root->right->parent = root;
    }

    return root;
}


void out(const auto& what, int n = 1) { while (n-- > 0) std::cout << what; }
void print(auto rem, auto const& v) {
    out(rem);
    for (auto e : v) { out(e), out(' '); }
    out('\n');
}



// TODO : fix print of empty tree nodes
void draw_tree(auto root){

    if(!root) return;

    using TreeTear = std::vector<decltype (root)>;
    std::stack <TreeTear> s;
    s.push({root});

    auto bails = [](int n, int w) {
        auto b = [](int w) { out("┌"), out("─", w), out("┴"), out("─", w), out("┐"); };
        if (!(n /= 2)) return;
        for (out(' ', w); n-- > 0; ) b(w), out(' ', w + w + 1);
        out('\n');
    };
    auto data = [](int n, int w, auto& first, auto last) {
        for(out(' ', w); n-- > 0 && first != last; ++first)
            out((*first)->val), out(' ', w + w + 1);
        out('\n');
    };
    auto print_tier = [&](int t, int m, auto& first, auto last) {
        const int n {1 << t};
        const int w {(1 << (m - t - 1)) - 1};
        bails(n, w), data(n, w, first, last);
    };

    const int m {static_cast<int>(std::ceil(std::log2(2 + root->child_count)))};

    auto i = 0;
    while(!s.empty()) {

        TreeTear tear;

        TreeTear top = s.top();

        auto first {top.cbegin()};
        print_tier(i++, m, first, top.cend());

        for(auto const& n: s.top()){
            if(n->left)tear.push_back(n->left);
            if(n->right)tear.push_back(n->right);
        }

        s.pop();

        if(!tear.empty())
        {
            s.push(std::move(tear));
        }
    }
}