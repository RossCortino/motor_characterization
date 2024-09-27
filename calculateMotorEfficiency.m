function [eta, Vq, Iq, torque, velocity] = calculateMotorEfficiency(file_path, motor_model)

    data_files = dir(fullfile(file_path,'*.xlsx'));
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

    driving_flag = ismember(temp_table.on_target,1) & ismember(temp_table.driving_motor,1);
    driven_flag = ismember(temp_table.on_target,1) & ismember(temp_table.driving_motor,2);

    driven_table = sortrows(temp_table(driven_flag,:),"velocity_command");
    driving_table = sortrows(temp_table(driving_flag,:),"velocity_command");

    driven_table_avg = groupsummary(driven_table,{'velocity_command'},...
        {'mean','std'}, {'measured_velocity_RI8523', 'measured_current_RI8523','measured_torque'});
    driving_table_avg = groupsummary(driving_table,{'velocity_command'},...
        {'mean','std'}, {'measured_velocity_RI8523', 'measured_current_RI8523','measured_torque'});

    k_t_q = motor_model.torque_model.k_t;
    b_m = motor_model.torque_model.b_m;
    f_m = motor_model.torque_model.b_m;
    R_phase = (3/2)*motor_model.R_ll;
    
    Vq_driving = k_t_q.*RPMtoradpersecond(driving_table_avg.mean_measured_velocity_RI8523)...
        + R_phase.*driving_table_avg.mean_measured_current_RI8523;
    Vq_driven = -k_t_q.*RPMtoradpersecond(driven_table_avg.mean_measured_velocity_RI8523)...
        + R_phase.*driven_table_avg.mean_measured_current_RI8523;
    
    eta_driving = driving_table_avg.mean_measured_torque...
        .*RPMtoradpersecond(driving_table_avg.mean_measured_velocity_RI8523)...
        /(Vq_driving.*driving_table_avg.mean_measured_current_RI8523);
    eta_driven = driven_table_avg.mean_measured_torque...
        .*RPMtoradpersecond(driven_table_avg.mean_measured_velocity_RI8523)...
        /(Vq_driven.*driven_table_avg.mean_measured_current_RI8523);

    eta = [eta_driving; eta_driven];
    Vq = [Vq_driving; Vq_driven];
    Iq = [Vq_driving; Iq_driven];
    torque = [driving_table_avg.mean_measured_torque; driven_table_avg.mean_measured_torque];
    velocity = [driving_table_avg.mean_measured_velocity_RI8523; driven_table_avg.mean_measured_velocity_RI8523];
end