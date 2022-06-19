for t in np.arange(dt,tmax,dt):
#     print(f"t={t} G={G} M={M_earth} z={z}")
    g = (G*M_earth)/((z+R_earth) ** 2)  # gravitational acceleration, g(z)
    m = m - (dm*dt)  # changing mass, m(t)
    rho,temp,press = density(z) # changing air density by barometric formula, rho(z)
    Cd = CD(v,temp,C0)
    thrust = FT/m
    drag = 0.5*rho*(v**2)*Cd*A/m
    
    if v < 0:  # flip drag force vector if rocket falls
        drag = drag*-1
        
    v = v + (thrust - drag - g)*dt  # new velocity
    z = z + v*dt  # new altitude
    
    V.append(v)
    Z.append(z)
    M.append(m)
    grav.append(g)
    Thrust.append(thrust)
    Drag.append(drag)
    Rho.append(rho)
    T.append(temp)
    P.append(press)
    t1=t
    if z < 0:  # rocket crashes or fails to launch
        print("Rocket fail z=",z)
        break
    elif m < empty:  # rocket runs out of fuel, mass becomes stable
        FT = 0
        dm = 0
print("done")


