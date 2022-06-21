__kernel void primes_atomic(int arr_size, __global float* final) {
    int gl_size = get_global_size(0);
    int gl_id = get_global_id(0);

    for(int idx_to_check = gl_id; idx_to_check <= arr_size; idx_to_check += gl_size){
        // printf("KERNEL (gl_id=%d) value %d ON IDX %d\n", gl_id, final[idx_to_check], idx_to_check);
        final[idx_to_check] = 1 / (1+pow((idx_to_check-0.5)/arr_size, 2));
        // printf("KERNEL (gl_id=%d) value %d ON IDX %d\n", gl_id, final[idx_to_check], idx_to_check);

    }

}