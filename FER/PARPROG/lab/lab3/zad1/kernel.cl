__kernel void primes(__global int* values, int arr_size, __global int* final) {
    int gl_size = get_global_size(0);
    int gl_id = get_global_id(0);
    // printf("(gl_id=%d)(gl_size=%d)(loc_size=%d)\n", gl_id, gl_size, loc_size);
    // for(int i = 0; i <= arr_size; ++i) printf("(gl_id=%d) for i=%d value=%d\n", gl_id, i, values[i]);

    for(int idx_to_check = gl_id; idx_to_check <= arr_size; idx_to_check += gl_size){
        int num_to_check = values[idx_to_check];
        // printf("KERNEL (gl_id=%d) NUM CHECK %d ON IDX %d\n", gl_id, num_to_check, idx_to_check);

        if(num_to_check < 2) continue;

        int isPrime = 1;

        for(int i = 2; i <= /*num_to_check */ (int) sqrt((double)num_to_check); ++i) {
            if (num_to_check % i == 0) {
                isPrime = 0;
                break;
            }
        }

        if (isPrime == 1){
            // printf("%d is prime\n", num_to_check);
            *final += 1;
            // atomic_inc(final);
        } else {
            // printf("%d is NOT prime\n", num_to_check);

        }
    }

    // printf("KERNEL RESULT IS %d\n", *final);
}

__kernel void primes_atomic(__global int* values, int arr_size, __global int* final) {
    int gl_size = get_global_size(0);
    int gl_id = get_global_id(0);
    // printf("(gl_id=%d)(gl_size=%d)(loc_size=%d)\n", gl_id, gl_size, loc_size);
    // for(int i = 0; i <= arr_size; ++i) printf("(gl_id=%d) for i=%d value=%d\n", gl_id, i, values[i]);

    for(int idx_to_check = gl_id; idx_to_check <= arr_size; idx_to_check += gl_size){
        int num_to_check = values[idx_to_check];
        // printf("KERNEL (gl_id=%d) NUM CHECK %d ON IDX %d\n", gl_id, num_to_check, idx_to_check);

        if(num_to_check < 2) continue;

        int isPrime = 1;

        for(int i = 2; i <= /*num_to_check */ (int) sqrt((double)num_to_check); ++i) {
            if (num_to_check % i == 0) {
                isPrime = 0;
                break;
            }
        }

        if (isPrime == 1){
            // printf("%d is prime\n", num_to_check);
            // *final += 1;
            atomic_inc(final);
        } else {
            // printf("%d is NOT prime\n", num_to_check);

        }
    }

    // printf("KERNEL RESULT IS %d\n", *final);
}