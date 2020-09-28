#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define len(x)  (sizeof(x) / sizeof((x)[0]))

double B(int *arr, int i, int j, double t){
    if(j == 0){
        return arr[i];
    }else{
        return B(arr, i, j - 1, t) * (1 - t) + B(arr, i + 1, j - 1, t) * t;
    }
}

void main() {
    int control_x[] = {1, 10, 14, 8};
    int control_y[] = {5, 15, 3, 5};
    double num_of_points = 1000;

    int n = len(control_x);

    double x[(int)num_of_points];
    for(int t = 0; t < num_of_points; t++){
        x[t] = B(control_x, 0, n - 1, ((double)t)/num_of_points);
    }

    double y[(int)num_of_points];
    for(int t = 0; t < num_of_points; t++){
        y[t] = B(control_y, 0, n - 1, ((double)t)/num_of_points);
    }

    for(int i = 0; i < num_of_points; i++){
        printf("x = %g, ", x[i]);
        printf("y = %g\n", y[i]);
    }

}

