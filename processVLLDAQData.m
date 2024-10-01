clear all
close all
addpath("Utility Functions\")


file_path = "data/V_LL_test/20240930/";


data_files = dir(fullfile(file_path,'*RPM.mat'));

if exist(strcat(file_path,"V_LL_processed.mat"),"file")
    load(strcat(file_path,"V_LL_processed.mat"))
else
    data = struct;
end

for f = 1:length(data_files)
    temp_str = (split(data_files(f).name,'_'));
    target_vel = str2num(temp_str{3,:});

    temp_data = load(strcat(file_path,data_files(f).name))

    figure(1)
    plot(temp_data.data.Time,temp_data.data.Dev1_ai0)
    ylabel("V_LL")
    xlabel("Time(s)")
    [start_time, end_time] = pickStartandEnd();
    
    start_ind = find(seconds(temp_data.data.Time) >= round([start_time],3),1);
    end_ind = find(seconds(temp_data.data.Time) >= round([end_time],3),1);
    time_concat = temp_data.data.Time(start_ind:end_ind);
    V_ll_concat = temp_data.data.Dev1_ai0(start_ind:end_ind);

    [V_ll_pks,locs] = findpeaks(abs(V_ll_concat));
    V_ll_avg = nanmean(V_ll_pks);
    figure(2)
    plot(time_concat,V_ll_concat)
    hold on
    scatter(time_concat(locs),V_ll_concat(locs),'filled')
    yline(V_ll_avg,'k-','LineWidth',2)
    hold off

    data.target_vel(f) = target_vel;
    data.V_ll_avg(f) = V_ll_avg;


end

save(strcat(file_path,"V_LL_processed.mat"),"data")


function [start_point,end_point] = pickStartandEnd()

input('Scale plot to start of steady state.');
disp('Select on point.');
[start_point, ~] = ginput(1);
disp('Start Index: ' + string(start_point));

input('Scale plot to end of steady state.');
disp('Select on point.');
[end_point, ~] = ginput(1);
disp('end_ind: ' + string(end_point));
end