//    1
//  ┌─┴─┐
//  2   3
// ┌┴┐ ┌┴┐
// 4 5

// Depth First Traversals:
// (a) Inorder (Left, Root, Right) : 4 2 5 1 3
// (b) Preorder (Root, Left, Right) : 1 2 4 5 3
// (c) Postorder (Left, Right, Root) : 4 5 2 3 1

// TASK INORDER


#include "binary_tree.hpp"
#include <assert.h>


using namespace std;


int treeHeight (auto root) {

    if(!root) return 0;

    auto hleft = treeHeight(root->left);
    auto hright = treeHeight(root->right);

    cerr << "val : "<<root->val << "  hleft:" << hleft << "  hright:"<< hright<< endl;

    if(hleft < 0 || hright < 0) return -1;

    if(std::abs(hleft - hright) > 1) return -1;

    return max(hleft, hright ) + 1;
}




int main()
{
    vector h {3,9,20,33,33,15,7};
   // ranges::make_heap(h, std::greater{});

    auto tree = make_tree(h);

    tree->left->left.reset();
    tree->left->right.reset();
    draw_tree(tree);

    auto result = treeHeight(tree);
    cerr << "result : " << result  << endl;
}


