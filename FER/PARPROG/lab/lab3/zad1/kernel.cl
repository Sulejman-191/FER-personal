kernel bool isPrime(int num_to_check)
{
    if(num_to_check <= 1)
        return false;

    for(int i = 2; i <= sqrt(num_to_check); ++i) {
        if (num_to_check % i == 0) return false;
    }
    return true;
}
