clc;
clear;
close all;

% USE 'FS' MODE

% filename = "Futek_ADC-PCB";
log_folder = "data/V_LL_test";
filename = strcat(log_folder,"/","V_LL_-400_RPM");

daqreset;
temp_dev = daqlist("ni");
dev = temp_dev(~contains(temp_dev.DeviceID,'Sim'),:);
assert(height(dev)==1);
disp("Reading device:");
disp(dev.Description);

dq = daq("ni");
dq.Rate = 500; % Flir @ 8.7Hz
[ch1,idx1] = addinput(dq, dev.DeviceID, "ai0", "Voltage");
ch1.Range = [-10 10];

logData(dq, filename);

function logData(dq, filename)

    stopClean = @() stopSave(filename);
    cleanup = onCleanup(stopClean);

    daq = dq;
    
    figure(1);
    xlabel('Time (sec)');
    ylabel('Voltage (V)');
    
    start(daq, "continuous");
    
    data = [];
    while true

        pause(5);
        data = [data; read(daq, "all")];
        plot(data.Time, data.Dev1_ai0);
        drawnow;
    
    end
    
    function stopSave(filename)

        stop(daq);
        data = [data; read(daq, "all")];
        disp('Stopped DAQ');
        save(filename, 'data');
%         save("TESTTESTTEST.mat", 'data');
        disp('Saved Data');
    
    end

end