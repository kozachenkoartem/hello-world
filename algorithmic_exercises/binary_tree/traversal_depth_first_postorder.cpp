//    1
//  ┌─┴─┐
//  2   3
// ┌┴┐ ┌┴┐
// 4 5

// Depth First Traversals:
// (a) Inorder (Left, Root, Right) : 4 2 5 1 3
// (b) Preorder (Root, Left, Right) : 1 2 4 5 3
// (c) Postorder (Left, Right, Root) : 4 5 2 3 1

// TASK POSTORDER


#include "binary_tree.hpp"
#include <assert.h>


using namespace std;

vector<int> postorderTraversal(auto root) {

    if(!root){
        return {};
    }

    vector<int> result;

    if(root->left) { // check to avoid axtra vector creation
        for(auto n : postorderTraversal(root->left)){
            result.push_back(n);
        }
    }

    if(root->right) {
        for(auto n : postorderTraversal(root->right)){
            result.push_back(n);
        }
    }
    result.push_back(root->val);

    return result;
}


vector<int> postorderTraversalIterative(auto root) {

    vector<int> result;
    auto prev = root;
    auto p = root;

    while(true) {
        if(!p->left && !p->right) {
            result.push_back(p->val);
            prev = p;
            p = p->parent.lock();
            //cerr << "go up"<< endl;
        }

        if(prev != p->left && prev != p->right) {

            if(p->left) {
                //cerr << "go left"<< endl;
                p = p->left;
            } else if(p->right){
                //cerr << "go right"<< endl;
                p = p->right;
            }
        } else if (prev == p->left && p->right) {
                //cerr << "go right"<< endl;
                p = p->right;
        } else if(prev == p->right || !p->right) {
            result.push_back(p->val);
            prev = p;
            //cerr << "go up"<< endl;
            p = p->parent.lock();
            if(!p) {
                break;
            }
        }
    }

    return result;
}

int main()
{
    vector h {1, 2, 3, 4, 5};
    vector expected {4, 5, 2, 3, 1};
    ranges::make_heap(h, std::greater{});

    auto tree = make_tree(h);
    draw_tree(tree);

    auto result = postorderTraversal(tree);
    auto iterative_result = postorderTraversalIterative(tree);

    print("expected result: ", expected);
    print("         result: ", result);
    print("iterative_result: ", iterative_result);

    assert(result == expected);
    assert(iterative_result == expected);
    out("OK\n");

}