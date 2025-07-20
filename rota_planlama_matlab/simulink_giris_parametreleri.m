% Fiziksel parametreler
m = 50;           % kütle (kg)
Iz = 10;          % z-ekseni atalet momenti
X_damp = 5;       % X yönü sürtünme
Y_damp = 20;      % Y yönü sürtünme
N_damp = 1;       % yaw sürtünme

% Baþlangýç pozisyonu ve hýzý
init_pose = [0; 0; 0];  % x, y, psi
init_vel  = [0; 0; 0];  % u, v, r

% Hedef nokta
target = [50; 30];      % x, y hedef konumu

% PID kazançlarý (yön kontrolü için)
Kp = 10;
Kd = 5;
