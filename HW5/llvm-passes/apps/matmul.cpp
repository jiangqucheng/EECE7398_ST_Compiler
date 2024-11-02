// matmul.cpp
#include <iostream>
#include <vector>

void matmul(int n) {
    std::vector<std::vector<int>> A(n, std::vector<int>(n, 1));
    std::vector<std::vector<int>> B(n, std::vector<int>(n, 2));
    std::vector<std::vector<int>> C(n, std::vector<int>(n, 0));

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            for (int k = 0; k < n; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }

    // Print a single value to check correctness
    std::cout << "C[0][0] = " << C[0][0] << std::endl;
}

int main() {
    int n = 100; // matrix dimension
    matmul(n);
    return 0;
}
