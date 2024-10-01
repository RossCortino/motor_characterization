clear all
close all
addpath("Utility Functions\")
%% Calculate kt from Locked motor test
kt_test_date = "2024_09_16";
kt_locked = calculateTorqueConstant(strcat("data/current_test/",kt_test_date),...
    false);

%% Calculate Kt from V_LL test
V_ll_test_date = "20240930";
[kt_V_ll] = calculateTorqueConstant_V_ll(strcat("data/V_LL_test/",V_ll_test_date));

%% Calculate viscous damping and friction from spinning motor test
velocity_test_date = "20240930";
[~, b_m_locked, f_locked] = calculateViscousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_locked);

[~, b_m_V_ll, f_V_ll] = calculateViscousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_V_ll);

%% Calculate Kt, b_m, and f_m from efficiency test
efficiency_test_date = "20240926";
[kt_const_vel, b_const_vel, f_m_const_vel] = calculateViscousDampingAndFriction_efficiency(strcat("data/efficiency_test/driven/",efficiency_test_date));
%% Calculate Efficiency

%% Plot Results

% Motor Characteristics across tests