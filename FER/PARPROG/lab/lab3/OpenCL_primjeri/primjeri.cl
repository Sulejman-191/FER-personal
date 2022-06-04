kernel void vektor(global int *A, global int *B, const int n) 
{
    // dohvati indeks
    int i = get_global_id(0);
	if (i > n) return;

    B[i] = A[i] * i;
}



kernel void get_id() 
{
	uint dim = get_work_dim();

	if(dim == 1) {
		int gid = get_global_id(0);
		int lid = get_local_id(0);

		printf("(%d)(%d)\t", lid, gid);
	}

	if(dim == 2) {
		int g0 = get_global_id(0);
		int g1 = get_global_id(1);
		int l0 = get_local_id(0);
		int l1 = get_local_id(1);

		printf("(%d,%d)(%d,%d)\t", l0, l1, g0, g1);
	}

}
