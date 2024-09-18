function [kt, b_m, f] = calculateViscuousDampingAndFriction(file_path,plot_flag, kt)

if isempty(kt)
    model_num = 2;
end

data_files = dir(fullfile(file_path,'*.csv'));

temp_table = [];
for k = 1:length(data_files)
    if isempty(temp_table)
        temp_table = readtable(strcat(data_files(k).folder,"\",data_files(k).name));

    else
        temp_table = [temp_table; readtable(strcat(data_files(k).folder,"\",data_files(k).name))];
    end
end
temp_table.Properties.VariableNames = ["time","motor_name",...
    "command","on_target","measured_velocity",...
    "measured_current"];

motor_on_flag = ismember(temp_table.on_target,1);

test_table = sortrows(temp_table(motor_on_flag,:),"command");
average_test_table = groupsummary(test_table,{'command'},{'mean','std'},{'measured_velocity','measured_current'});

switch model_num
    case 1
        A_all = [RPM_to_radpersecond(test_table.measured_velocity),...
            sign(test_table.measured_velocity)];
        b_all = [-kt.*test_table.measured_current];

        A_avg = [RPM_to_radpersecond(average_test_table.mean_measured_velocity),...
            sign(average_test_table.mean_measured_velocity)];
        b_avg = [-kt.*average_test_table.mean_measured_current];

        x_all = least_squares(A_all,b_all);
        x_avg = least_squares(A_avg, b_avg);

        b_m = x_avg(1);
        f = x_avg(2);
    case 2
        A_all = [test_table.measured_current, ...
                -RPM_to_radpersecond(test_table.measured_velocity),...
                -sign(test_table.measured_velocity)];
        b_all = zeros(size(test_table.measured_current));

        A_avg = [average_test_table.measured_current, ...
                -RPM_to_radpersecond(average_test_table.mean_measured_velocity),...
                -sign(average_test_table.mean_measured_velocity)];
        b_avg = zeros(size(average_test_table.mean_measured_current));

        x_all = least_squares(A_all,b_all);
        x_avg = least_squares(A_avg, b_avg);
        
        kt = x_avg(1);
        b_m = x_avg(2);
        f = x_avg(3);
end


end

