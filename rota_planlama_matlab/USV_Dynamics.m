function dx = USV_Dynamics(x, u_input)

    global m Iz X_damp Y_damp N_damp

    psi = x(3); u = x(4); v = x(5); r = x(6);
    Fx = u_input(1); Fy = u_input(2); Mz = u_input(3);

    dx = zeros(6,1);
    dx(1) = u*cos(psi) - v*sin(psi);
    dx(2) = u*sin(psi) + v*cos(psi);
    dx(3) = r;
    dx(4) = (1/m)*(Fx - X_damp*u);
    dx(5) = (1/m)*(Fy - Y_damp*v);
    dx(6) = (1/Iz)*(Mz - N_damp*r);
end
