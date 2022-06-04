c File fpotencial.f
       subroutine fpotencial (dimx, dimy)
    
cf2py  integer, intent(in) :: dimx
cf2py  integer, intent(in) :: dimy

       do i=0, dimx
           do j=0, dimy
               print*,  i, " ", j 
           end do
       end do
       end
