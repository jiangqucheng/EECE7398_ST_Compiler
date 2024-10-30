#include <stdio.h>
void logop(int i) {
    printf("logop computed: %i\n", i);
}

void logfdiv(float dest, float lhs, float rhs) {
    printf("logfdiv: %f = %f / %f\n", dest, lhs, rhs);
}
