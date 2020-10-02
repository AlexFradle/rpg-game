#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#define len(x)  (sizeof(x) / sizeof((x)[0]))

#ifndef NUMBER_OF_POINTS
#define NUMBER_OF_POINTS 1000
#endif

double B(int *arr, int i, int j, double t){
    if(j == 0){
        return arr[i];
    }else{
        return B(arr, i, j - 1, t) * (1 - t) + B(arr, i + 1, j - 1, t) * t;
    }
}


double * get_x(int *control_x, int num_of_control){
    int n = num_of_control;

    static double x_points[NUMBER_OF_POINTS];
    for(int t = 0; t < NUMBER_OF_POINTS; t++){
        x_points[t] = B(control_x, 0, n - 1, ((double)t)/((double)NUMBER_OF_POINTS));
    }
    return x_points;
}


double * get_y(int *control_y, int num_of_control){
    int n = num_of_control;

    static double y_points[1000];
    for(int t = 0; t < NUMBER_OF_POINTS; t++){
        y_points[t] = B(control_y, 0, n - 1, ((double)t)/((double)NUMBER_OF_POINTS));
    }
    return y_points;
}

void main(){
    return;
}

// void main() {
//     int control_x[] = {1, 10, 14, 8};
//     int control_y[] = {5, 15, 3, 5};
//     double num_of_points = 1000;

//     // int n = len(control_x);

//     // double x[(int)num_of_points];
//     // for(int t = 0; t < num_of_points; t++){
//     //     x[t] = B(control_x, 0, n - 1, ((double)t)/((double)num_of_points));
//     // }

//     // double y[(int)num_of_points];
//     // for(int t = 0; t < num_of_points; t++){
//     //     y[t] = B(control_y, 0, n - 1, ((double)t)/((double)num_of_points));
//     // }

//     double *x;
//     double *y;

//     x = get_x(control_x, num_of_points);
//     y = get_y(control_y, num_of_points);

//     for(int i = 0; i < num_of_points; i++){
//         printf("x = %g, ", x[i]);
//         printf("y = %g\n", y[i]);
//     }

// }

