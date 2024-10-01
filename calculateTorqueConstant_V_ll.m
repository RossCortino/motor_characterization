function k_t = calculateTorqueConstant_V_ll(file_path)
        
    data_files = dir(fullfile(file_path,'*.csv'));
    V_ll_data = load(strcat(file_path,"/V_LL_processed.mat"))

    V_ll_table = struct2table(V_ll_data.data);

    temp_table = [];
    for f = 1:length(data_files)
        if isempty(temp_table)
            temp_table = readtable(strcat(data_files(f).folder,"\",data_files(f).name));
    
        else
            temp_table = [temp_table; readtable(strcat(data_files(f).folder,"\",data_files(f).name))];
        end
    end

     temp_table.Properties.VariableNames = ["time","motor_name",...
                "commanded_velocity","on_target","measured_velocity",...
                "measured_current"];
    motor_on_flag = ismember(temp_table.on_target,1);


    test_table = sortrows(temp_table(motor_on_flag,:),"commanded_velocity");
    average_test_table = groupsummary(test_table,{'commanded_velocity'},{'mean','std'},{'measured_velocity'});

    k_t_list = NaN(size(average_test_table,1),1);

    for ind = 1:size(average_test_table,1)
        com_vel = average_test_table.commanded_velocity(ind);
        meas_vel = average_test_table.mean_measured_velocity(ind);
        V_ll = V_ll_table.V_ll_avg(V_ll_table.target_vel == com_vel);
        k_t_list(ind) = abs(sqrt(3/2)*V_ll*(1/RPM_to_radpersecond(meas_vel)));
        
    end

    figure
    plot(average_test_table.commanded_velocity,k_t_list)

    k_t = mean(k_t_list,'omitmissing');
end