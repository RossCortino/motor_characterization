clear all
close all
addpath("Utility Functions\")
%% Calculate Torque Constant from Locked motor test
kt_test_date = "2024_09_16";
kt_locked = calculateTorqueConstant(strcat("data/current_test/",kt_test_date),...
    false);

%% 10 RPM : Calculate viscous damping and friction from spinning motor test
velocity_test_date = "2024_09_20/ten_rpm_test";
[~, b_m_known_10, f_known_10] = calculateViscuousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_locked);
% [kt_unknown_10, b_m_unknown_10, f_unknown_10] = calculateViscuousDampingAndFriction(strcat(...
%     "data/velocity_test/velocity_control/", velocity_test_date), false);

%% 100 RPM : Calculate viscous damping and friction from spinning motor test
velocity_test_date = "2024_09_20/hundred_rpm_test";
[~,b_m_known_100, f_known_100] = calculateViscuousDampingAndFriction(strcat(...
    "data/velocity_test/velocity_control/", velocity_test_date), true, kt_locked);
% [kt_unknown_100, b_m_unknown_100, f_unknown_100] = calculateViscuousDampingAndFriction(strcat(...
%     "data/velocity_test/velocity_control/", velocity_test_date), false);
