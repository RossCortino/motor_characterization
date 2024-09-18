clear all
close all

%% Calculate Torque Constant from Locked motor test
kt_test_date = "2024_09_16";
kt_locked = calculateTorqueConstant(strcat("data/current_test/",kt_test_date), false);

%% Calculate viscous damping and friction from spinning motor test
velocity_test_date = "";
[b_m, f] = calculateViscuousDampingAndFriction(strcat("data/velocity_test/",velocity_test_date),false);