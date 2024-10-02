function [k_t, b_m, f] = calculateViscousDampingAndFriction_efficiency(file_path)

data_files = dir(fullfile(file_path,'*.csv'));
% data_files.folder
temp_table = [];
for k = 1:length(data_files)
    if isempty(temp_table)
        temp_table = readtable(strcat(data_files(k).folder,"\",data_files(k).name));

    else
        temp_table = [temp_table; readtable(strcat(data_files(k).folder,"\",data_files(k).name))];
    end
end

temp_table.Properties.VariableNames = ["time","driving_motor",...
    "current_command","velocity_command","on_target","measured_velocity_MN1005",...
    "measured_velocity_RI8523","measured_current_MN1005", "measured_current_RI8523",...
    "measured_torque"];

motor_on_flag = ismember(temp_table.on_target,1); %& ~(abs(temp_table.velocity_command) == 0);

test_table = sortrows(temp_table(motor_on_flag,:),"velocity_command");
average_test_table = groupsummary(test_table,{'velocity_command','current_command'},{'mean','std'},...
    {'measured_velocity_RI8523','measured_current_RI8523','measured_torque'});


A_all = [test_table.measured_current_RI8523, -RPM_to_radpersecond(test_table.measured_velocity_RI8523),...
    -sign(RPM_to_radpersecond(test_table.measured_velocity_RI8523)), ones(size(test_table.measured_current_RI8523))];
b_all = test_table.measured_torque;

A_test = [test_table.measured_current_RI8523, -RPM_to_radpersecond(test_table.measured_velocity_RI8523),...
    sign(test_table.measured_current_RI8523), ones(size(test_table.measured_current_RI8523))];

A_avg = [average_test_table.mean_measured_current_RI8523, -RPM_to_radpersecond(average_test_table.mean_measured_velocity_RI8523),...
    -sign(RPM_to_radpersecond(average_test_table.mean_measured_velocity_RI8523)), ones(size(average_test_table.mean_measured_current_RI8523))];
b_avg = average_test_table.mean_measured_torque; % + .038*sign(average_test_table.mean_measured_velocity_RI8523);
lb = [0 0 0 -inf]';
ub = [inf inf inf inf]';
x_all = least_squares(A_all,b_all);
x_all_bound = lsqlin(A_all, b_all,[], [], [], [], lb, ub);
x_avg_nobound = least_squares(A_avg, b_avg);
x_avg_bound = lsqlin(A_avg, b_avg,[], [], [], [], lb, ub); %least_squares(A_avg, b_avg);

figure
plot(average_test_table.mean_measured_torque, LineWidth=2)
hold on
plot(A_avg*x_avg_bound, LineWidth=2)
plot(A_avg*x_avg_nobound, LineWidth=2)

legend("Measured","Bound Model", "Unbound Model")

vaf_bound = VAF(average_test_table.mean_measured_torque, A_avg*x_avg_bound)

vaf_unbound = VAF(average_test_table.mean_measured_torque, A_avg*x_avg_nobound)

k_t_all = x_all(1);
b_m_all = x_all(2);
f_all = x_all(3);

k_t_avg = x_avg_bound(1);
b_m_avg = x_avg_bound(2);
f_avg = x_avg_bound(3);

k_t = k_t_avg;
b_m = b_m_avg;
f = f_avg;


end