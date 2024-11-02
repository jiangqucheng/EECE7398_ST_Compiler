#include <stdio.h>

int test2() {
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += i;
    }
    printf("Sum: %d\n", sum);
    return 0;
}

// int test1() {
//     int jjj = 0;
//     for (int i = 0; i < 100; i++) {
//         for (int k = 0; k < 100; k++) {
//             jjj += i;
//             jjj -= (i-1);
//             jjj *= (i%10);
//         }
//     }
//     printf("%i\n", jjj);
//     return 0;
// }

int main(int argc, const char** argv) {
    // test1();
    test2();
    return 0;
}

