//    1
//  ┌─┴─┐
//  2   3
// ┌┴┐ ┌┴┐
// 4 5

// Level order traversal of the above tree is 1 2 3 4 5

#include <queue>
#include <assert.h>
#include "binary_tree.hpp"

using namespace std;

vector<int>  BreadthFirstTraversal(auto root) {
	std::queue<decltype(root)> q;
	q.push(root);

	vector<int> result;

	while(!q.empty()){
		const auto &top = q.front();
		result.push_back(top->val);
		if(top->left)q.push(top->left);
		if(top->right)q.push(top->right);
		q.pop();
	}

	return result;
}

int main()
{
	vector h {1, 2, 3, 4, 5};
    vector expected = h;
    ranges::make_heap(h, std::greater{});

    auto tree = make_tree(h);
    draw_tree(tree);

    auto result = BreadthFirstTraversal(tree);

    print("expected result: ", expected);
    print("         result: ", result);

    assert(result == expected);

     out("OK\n");
	return 0;
}