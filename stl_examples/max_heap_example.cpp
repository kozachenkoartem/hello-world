#include <algorithm>
#include <vector>
#include <cmath>
#include <functional>
#include <iostream>

void draw_heap(auto const& v);
void out(const auto& what, int n = 1) { while (n-- > 0) std::cout << what; }
void print(auto rem, auto const& v) {
    out(rem);
    for (auto e : v) { out(e), out(' '); }
    out('\n');
}

int main()
{
    std::vector h {1, 6, 1, 8, 0, 3, 3, 9, 8, 8, 7, 4, 9, 8, 9};
    print("  source: ", h);

    std::ranges::make_heap(h);
    print("\n" "min-heap: ", h);
    draw_heap(h);


    h.push_back(22);
    print("\n" "before push: ", h);
    draw_heap(h);

    std::ranges::push_heap(h);
    print("\n" "after push: ", h);
    draw_heap(h);

}

void draw_heap(auto const& v)
{
    auto bails = [](int n, int w) {
        auto b = [](int w) { out("┌"), out("─", w), out("┴"), out("─", w), out("┐"); };
        if (!(n /= 2)) return;
        for (out(' ', w); n-- > 0; ) b(w), out(' ', w + w + 1);
        out('\n');
    };
    auto data = [](int n, int w, auto& first, auto last) {
        for(out(' ', w); n-- > 0 && first != last; ++first)
            out(*first), out(' ', w + w + 1);
        out('\n');
    };
    auto tier = [&](int t, int m, auto& first, auto last) {
        const int n {1 << t};
        const int w {(1 << (m - t - 1)) - 1};
        bails(n, w), data(n, w, first, last);
    };
    const int m {static_cast<int>(std::ceil(std::log2(1 + v.size())))};

    print("m:", std::vector{m});
    auto first {v.cbegin()};
    for (int i{}; i != m; ++i) { tier(i, m, first, v.cend()); }
}