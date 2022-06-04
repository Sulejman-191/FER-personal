C File  temp.f
        subroutine pot(arr, error, dimx, dimy) 
    
        integer dimx
        integer dimy
        logical diff_condition
        double precision new_value 
        double precision arr(dimx, dimy)
        
cf2py   intent(inout) :: arr
cf2py   intent(in) :: error
cf2py   intent(in) :: dimx
cf2py   intent(in) :: dimy

        diff_condition = .false.
        new_value = 0
        
        print *, error, dimx, dimy, arr, diff_condition, new_value
        
        end
