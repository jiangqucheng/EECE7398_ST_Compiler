#include <stdio.h>
int main(int argc, const char** argv) {
    int num;
    printf("Enter a number: ");
    scanf("%i", &num);
    printf("%i\n", num + 2);
    printf("%i\n", num - 2);
    printf("%i\n", num * 2);
    printf("%i\n", num / 2);
    float fnum;
    printf("Enter a float number: ");
    scanf("%f", &fnum);
    printf("%f\n", fnum + 2.0);
    printf("%f\n", fnum - 2.0);
    printf("%f\n", fnum * 2.0);
    printf("%f\n", fnum / 2.0);
    return 0;
}
