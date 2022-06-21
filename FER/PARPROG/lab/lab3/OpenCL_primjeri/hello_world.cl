__kernel void hello_world(__global int* values, int tmp) {
    int global_id = get_global_id(0);
    printf("Hello Taiwan!!! from kernel #%d, got value: %d, tmp=%d\n", global_id, values[global_id], tmp);
}