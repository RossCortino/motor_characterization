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
[~, b_m_locked, f_m_locked] = calculateViscousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_locked);

[~, b_m_V_ll, f_m_V_ll] = calculateViscousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_V_ll);

%% Calculate Kt, b_m, and f_m from efficiency test
efficiency_test_date = "20240926";
[kt_const_vel, b_m_const_vel, f_m_const_vel] = calculateViscousDampingAndFriction_efficiency(strcat("data/efficiency_test/driven/",efficiency_test_date));
%% Calculate Efficiency

%% Plot Results


k_t = [kt_locked, kt_V_ll, kt_const_vel];
b_m = [b_m_locked, b_m_V_ll, b_m_const_vel];
f_m = [f_m_locked, f_m_V_ll, f_m_const_vel];
% Motor Characteristics across tests

Locked_Rotor_Test = [kt_locked; b_m_locked; f_m_locked];
V_LL_Test = [kt_V_ll; b_m_V_ll; f_m_V_ll];
Constant_Velocity_Test = [kt_const_vel; b_m_const_vel; f_m_const_vel];
Average_Value = [mean(k_t); mean(b_m); mean(f_m)];

motor_characteristic_table = table(Locked_Rotor_Test,V_LL_Test, Constant_Velocity_Test, Average_Value,'RowNames',{'k_t','b_m','f_m'});