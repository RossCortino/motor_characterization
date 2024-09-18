function kt = calculateTorqueConstant(file_path,plot_flag)
    % close all
    % file_path = "data/current_test/2024_09_16";

    data_files = dir(fullfile(file_path,'*.csv'));

    temp_table = [];
    for f = 1:length(data_files)
        if isempty(temp_table)
            temp_table = readtable(strcat(data_files(f).folder,"\",data_files(f).name));
            
        else
            temp_table = [temp_table; readtable(strcat(data_files(f).folder,"\",data_files(f).name))];
        end
    end
    temp_table.Properties.VariableNames = ["time","motor_name",...
                "commanded_current","on_target","motor_position",...
                "measured_current", "torque"];
    motor_on_flag = ismember(temp_table.on_target,1);

    test_table = sortrows(temp_table(motor_on_flag,:),"commanded_current");
    average_test_table = groupsummary(test_table,{'commanded_current'},{'mean','std'},{'measured_current','torque'});
    p_all = polyfit(temp_table.measured_current,temp_table.torque,1);
    p_avg = polyfit(average_test_table.mean_measured_current, average_test_table.mean_torque,1);

    plot_colors = getColors();
    x_poly = linspace(-10,10,100);
    y_poly_all = polyval(p_all,x_poly);
    y_poly_avg = polyval(p_avg,x_poly);

    % A = [average_test_table.mean_measured_current, ones(size(average_test_table.mean_measured_current))];
    % b = average_test_table.mean_torque;
    % 
    % x_ls = inv(A'*A)*A'*b;
    if plot_flag
        figure
        plot(test_table.measured_current,test_table.torque, "Marker","*","Color",plot_colors.wine)
        hold on
        plot(average_test_table.mean_measured_current, average_test_table.mean_torque,"Marker","o","Color",plot_colors.cyan)
        plot(x_poly,y_poly_all,"Color",plot_colors.rose,"LineWidth",2)
        plot(x_poly,y_poly_avg,"Color",plot_colors.teal,"LineWidth",2)
        legend("All Data", "Avg Data","Fit All","Fit Avg")
    end

    kt = p_avg(1);

    % figure
    % plot(temp_table.Var6, temp_table.Var7,'*')
    % p = polyfit(temp_table.Var6,temp_table.Var7,1);
    % hold on
    % x_test = linspace(-10,10,100);
    % plot(x_test,polyval(p,x_test),'LineWidth',2)

end