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

bool isSameTree(auto p, auto q) {



	if(!p && !q) return true;
	if(!p || !q) return false;
	if(p && q && (p->val != q->val)) {
		return false;
	}

	return isSameTree(p->left, q->left) && isSameTree(p->right, q->right);
}



int main()
{
    vector h {1, 2, 3, 5, 6, 7, 8, 9, 10};

    assert(isSameTree(make_tree(h), make_tree(h)));
    out("OK\n");

}


