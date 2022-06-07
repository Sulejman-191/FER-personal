__kernel void jacobistep(double *psinew, double *psi, int m, int n) {
  int i = get_global_id(0), j = get_global_id(1);
  int gl_size = get_global_size(0);
  int gl_id = get_global_id(0);
  int loc_id = get_local_id(0);
  // printf("gl_id(0)=%d gl_id(1)=%d, %d, %d\n",
  // get_global_id(0),get_global_id(1), get_local_id(0), get_global_size(0));
  psinew[i * (m + 2) + j] =
      0.25 * (psi[(i - 1) * (m + 2) + j] + psi[(i + 1) * (m + 2) + j] +
              psi[i * (m + 2) + j - 1] + psi[i * (m + 2) + j + 1]);
  /*

    for(int idx_to_check = gl_id; idx_to_check <= arr_size; idx_to_check +=
    gl_size){
        psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
    }

    for(i=1;i<=m;i++) {
            for(j=1;j<=n;j++) {
            psinew[i*(m+2)+j]=0.25*(psi[(i-1)*(m+2)+j]+psi[(i+1)*(m+2)+j]+psi[i*(m+2)+j-1]+psi[i*(m+2)+j+1]);
            }
    }*/
}
