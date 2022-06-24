// Example program
#include <iostream>

using namespace std;
struct TreeNode {
  int val;
  TreeNode *left;
  TreeNode *right;
  TreeNode *parent;
  TreeNode() : val(0), left(nullptr), right(nullptr), parent(nullptr) {}
  TreeNode(int x) : val(x), left(nullptr), right(nullptr), parent(nullptr) {}
  TreeNode(int x,  TreeNode *parent) : val(x), left(nullptr), right(nullptr), parent(parent) {}
};

int maxDepth(TreeNode* root)
{
    if(root == nullptr) return 0;
    return 1+max(maxDepth(root->left),maxDepth(root->right));
}

int maxDepth1(TreeNode* root)
{
    auto prev = root;
    auto p = root;

    auto d = 1;
    auto maxd = 0;

    while(true) {

        if(!p->left && !p->right){
            if(d > maxd) maxd = d;
            prev = p;
            p = p->parent;
            d --;
        }

        if(prev != p->left && prev != p->right) {
            if(p->left) {
                p = p->left;
                d++;
            } else if(p->right){
                p = p->right;
                d++;
            }
        } else if (prev == p->left && p->right) {
                p = p->right;
                d++;
        } else if(prev == p->right || !p->right) {
            prev = p;
            p = p->parent;
            d --;
            if(d == 0) {
                break;
            }
        }

    }

    return maxd;

}


int main()
{
    TreeNode *root= new TreeNode(1);
    root->left = new TreeNode(2, root);
    root->left->left = new TreeNode(3, root->left);
    root->right= new TreeNode(4, root);
    root->right->left= new TreeNode(5, root->right);
    root->right->right= new TreeNode(6, root->right);
    root->right->right->right= new TreeNode(7, root->right->right);

    cout<<maxDepth(root)<<endl;
    cout<<maxDepth1(root)<<endl;
  return 0;
}
