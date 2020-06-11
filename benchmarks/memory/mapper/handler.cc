#include <iostream>
#include <chrono>
#include <random>

using namespace std;

static const size_t N_TRIALS = 128;

static const size_t ARRAY_SIZE = 1024 * 1024 * 8;
static double a[ARRAY_SIZE];
static double b[ARRAY_SIZE];
static double c[ARRAY_SIZE];

int main() {
    uniform_real_distribution<double> unif(1.0, 5.0);
    default_random_engine re;
    double a_random_double = unif(re);

    for (size_t j = 0; j < ARRAY_SIZE; j++) {
        a[j] = unif(re);
        b[j] = unif(re);
        c[j] = unif(re);
    }
    double scalar = unif(re);

    auto start = chrono::steady_clock::now();
    for (size_t i = 0; i < N_TRIALS; i++) {
        for (size_t j = 0; j < ARRAY_SIZE; j++) {
            a[j] += b[j] + c[j] * scalar;
        }
    }
    auto end = chrono::steady_clock::now();
    chrono::duration<double> elapsed = end - start;

    cout << elapsed.count() << endl;
    return 0;
}
