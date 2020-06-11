#include <iostream>
#include <chrono>

using namespace std;

int main() {
    double duration;
    cin >> duration;

    auto start = chrono::steady_clock::now();
    unsigned long long n = 0;
    while (true) {
        auto now = chrono::steady_clock::now();
        chrono::duration<double> elapsed = now - start;
        if (elapsed.count() > duration) break;
        n++;
    }

    cout << n << endl;
    return 0;
}
