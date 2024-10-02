% getStrideBiomechanics_R01.m
% Ross Cortino (cortinrj@umich.edu, rcortino3@gmail.com, 630-777-1046)
% 2023-04-17
% This script is for generating a struct containing, intersubject mean, std., and 
% matrix of all strides for a desired activity/stride/task(s) combination.
% This script has been validated for the activitiies/strides:
%   - Stair/s3 
%   - Stair/s1
% Activities/strides not evaluated may need debugging or added code to this script.
% As of now, stance and swing are split based on kinematic trends that signal toe-off.
% Future work can be done to parse data with GRF available. Refer to the stair
% configuration naming scheme shown in the Readme provided with the R01 Dataset. 

function dataOut = getStrideBiomechanics_R01(dataset,activity,stride,task_input)
% dataset (struct): R01 Normalized Dataset
% activity(string): Stair, ...
% stride(string): s1,s3,...
% task_input (string ) - optional: See task lists below

switch activity
    case "Stair"
        leaveOut = ["none"];
        task_list_temp = ["in35", "in30", "in25", "in20", "i20", "i25", "i30", "i35"];
    otherwise
        error("Please input valid activity from this list: Stair")
end


if ~exist('task_input','var')
    task_list = task_list_temp;
else
    task_list = task_input;
end

subject_fields = fieldnames(dataset);

segmentLengths = averageInterSubjectBodyDimensionsR01(dataset,subject_fields);

thigh_lengths = segmentLengths.thigh';
shank_lengths = segmentLengths.shank';

for j = 1:length(task_list)
    
    task = task_list(j);
    disp(strcat("Processing ",task))
    
    % Full Stride
    thigh_angle_task = [];
    knee_angle_task = [];
    ankle_angle_task = [];
    
    thigh_velocity_task = [];
    knee_velocity_task = [];
    ankle_velocity_task = [];
    
    knee_torque_task= [];
    ankle_torque_task = [];
    
    knee_power_task= [];
    ankle_power_task = [];
    
    stride_time_task = [];
    
    knee_work_task = [];
    ankle_work_task = [];

    TO_task_temp = [];
    MHE_task_temp = [];
    MHF_task_temp = [];
    HS_task_temp = [];

    
    % Stance Stride
    thigh_angle_task_stance = [];
    knee_angle_task_stance = [];
    ankle_angle_task_stance = [];
    
    thigh_velocity_task_stance = [];
    knee_velocity_task_stance = [];
    ankle_velocity_task_stance = [];
    
    knee_torque_task_stance = [];
    ankle_torque_task_stance = [];
    
    knee_power_task_stance = [];
    ankle_power_task_stance = [];
    
    stride_time_task_stance = [];
    
    knee_work_task_stance = [];
    ankle_work_task_stance = [];

    TO_task_temp_stance = [];
    MHE_task_temp_stance = [];
    MHF_task_temp_stance = [];
    HS_task_temp_stance = [];
    
    % Swing Stride
    thigh_angle_task_swing = [];
    knee_angle_task_swing = [];
    ankle_angle_task_swing = [];
    
    thigh_velocity_task_swing = [];
    knee_velocity_task_swing = [];
    ankle_velocity_task_swing = [];
    
    knee_torque_task_swing = [];
    ankle_torque_task_swing = [];
    stride_time_task_swing = [];

    TO_task_temp_swing= [];
    MHE_task_temp_swing = [];
    MHF_task_temp_swing = [];
    HS_task_temp_swing= [];

    for i = 1:length(subject_fields)
        
        subject = subject_fields{i};
        
        disp(strcat("    Processing ",subject))

        pelvis_angle_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngles.PelvisAngles;
        hip_angle_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngles.HipAngles;
        thigh_angle_sub_temp = hip_angle_sub_temp - pelvis_angle_sub_temp;
        knee_angle_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngles.KneeAngles;
        ankle_angle_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngles.AnkleAngles;

        pelvis_velocity_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngleVels.PelvisAngleVels;
        hip_velocity_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngleVels.HipAngleVels;
        thigh_velocity_sub_temp = hip_velocity_sub_temp - pelvis_velocity_sub_temp;
        knee_velocity_sub_temp =dataset.(subject).(activity).(stride).(task).jointAngleVels.KneeAngleVels;
        ankle_velocity_sub_temp = dataset.(subject).(activity).(stride).(task).jointAngleVels.AnkleAngleVels;

        pelvis_angle_sub = squeeze(pelvis_angle_sub_temp(:,1,:))';
        hip_angle_sub = squeeze(hip_angle_sub_temp(:,1,:))';
        thigh_angle_sub = squeeze(thigh_angle_sub_temp(:,1,:))';
        knee_angle_sub = squeeze(knee_angle_sub_temp(:,1,:))';
        ankle_angle_sub = squeeze(ankle_angle_sub_temp(:,1,:))';

        pelvis_velocity_sub = squeeze(pelvis_velocity_sub_temp(:,1,:))';
        hip_velocity_sub = squeeze(hip_velocity_sub_temp(:,1,:))';
        thigh_velocity_sub = squeeze(thigh_velocity_sub_temp(:,1,:))';
        knee_velocity_sub = squeeze(knee_velocity_sub_temp(:,1,:))';
        ankle_velocity_sub = squeeze(ankle_velocity_sub_temp(:,1,:))';

        %Event Indexes
        [MHE_val, MHE_ind] = min(thigh_angle_sub');
        [MHF_val, MHF_ind] = max(thigh_angle_sub');
        HS_ind = ones(size(thigh_angle_sub,1),1);
        
        MHE_sub = MHE_ind';
        MHF_sub = MHF_ind';
        HS_sub = HS_ind;
        TO_sub = NaN(size(thigh_angle_sub,1),1);

        
        stride_time_sub = NaN(size(thigh_angle_sub));
        
        
        % initialize stance data
        thigh_angle_sub_stance = NaN(size(thigh_angle_sub));
        knee_angle_sub_stance = NaN(size(thigh_angle_sub));
        ankle_angle_sub_stance = NaN(size(thigh_angle_sub));
        
        thigh_velocity_sub_stance = NaN(size(thigh_angle_sub));
        knee_velocity_sub_stance = NaN(size(thigh_angle_sub));
        ankle_velocity_sub_stance = NaN(size(thigh_angle_sub));

        stride_time_sub_stance = NaN(size(thigh_angle_sub));
        
        HS_sub_stance = NaN(size(thigh_angle_sub,1),1);
        MHE_sub_stance = NaN(size(thigh_angle_sub,1),1);
        TO_sub_stance = NaN(size(thigh_angle_sub,1),1);
        MHF_sub_stance = NaN(size(thigh_angle_sub,1),1);
        
        % initialize swing data
        thigh_angle_sub_swing = NaN(size(thigh_angle_sub));
        knee_angle_sub_swing = NaN(size(thigh_angle_sub));
        ankle_angle_sub_swing = NaN(size(thigh_angle_sub));
        
        thigh_velocity_sub_swing = NaN(size(thigh_angle_sub));
        knee_velocity_sub_swing = NaN(size(thigh_angle_sub));
        ankle_velocity_sub_swing = NaN(size(thigh_angle_sub));
        
        stride_time_sub_swing = NaN(size(thigh_angle_sub));
        
        HS_sub_swing = NaN(size(thigh_angle_sub,1),1);
        MHE_sub_swing = NaN(size(thigh_angle_sub,1),1);
        TO_sub_swing = NaN(size(thigh_angle_sub,1),1);
        MHF_sub_swing = NaN(size(thigh_angle_sub,1),1);
         
        for v = 1:size(thigh_angle_sub,1)
            thigh_angle_trial = thigh_angle_sub(v,:);
            knee_angle_trial = knee_angle_sub(v,:);
            ankle_angle_trial = ankle_angle_sub(v,:);
            
            thigh_velocity_trial = thigh_velocity_sub(v,:);
            knee_velocity_trial = knee_velocity_sub(v,:);
            ankle_velocity_trial = ankle_velocity_sub(v,:);

            stride_time_trial = linspace(0,dataset.(subject).(activity).(stride).(task).events.StrideDetails(v,3),length(thigh_angle_trial));
            
            if contains(task,"in")
                [~,swing_start] = max(knee_angle_trial);
            else
                [~,swing_start] = min(ankle_angle_trial);
            end
            TO_ind = swing_start-1;
            stance_ind = 1:TO_ind;
            swing_ind = TO_ind+1:length(thigh_angle_trial);
            sample_vec = 1:length(thigh_angle_trial);

            stride_time_sub(v,:) = stride_time_trial;
            % Stance
            thigh_angle_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),thigh_angle_trial(:,stance_ind),sample_vec);
            knee_angle_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),knee_angle_trial(:,stance_ind),sample_vec);
            ankle_angle_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),ankle_angle_trial(:,stance_ind),sample_vec);

            thigh_velocity_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),thigh_velocity_trial(:,stance_ind),sample_vec);
            knee_velocity_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),knee_velocity_trial(:,stance_ind),sample_vec);
            ankle_velocity_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),ankle_velocity_trial(:,stance_ind),sample_vec);
            
            [MHE_val_stance, MHE_ind_stance] = min(thigh_angle_sub_stance(v,:));

            HS_sub_stance(v,:) = 1;
            MHE_sub_stance(v,:) = MHE_ind_stance;
            TO_sub_stance(v,:) = length(thigh_angle_sub_stance(v,:));

            stride_time_sub_stance(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(stance_ind)),stride_time_trial(:,stance_ind),sample_vec);
            

            % Swing
            thigh_angle_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),thigh_angle_trial(:,swing_ind),sample_vec);
            knee_angle_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),knee_angle_trial(:,swing_ind),sample_vec);
            ankle_angle_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),ankle_angle_trial(:,swing_ind),sample_vec);

            thigh_velocity_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),thigh_velocity_trial(:,swing_ind),sample_vec);
            knee_velocity_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),knee_velocity_trial(:,swing_ind),sample_vec);
            ankle_velocity_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),ankle_velocity_trial(:,swing_ind),sample_vec);
            
            [MHF_val_swing, MHF_ind_swing] = max(thigh_angle_sub_swing(v,:));
            MHF_sub_swing(v,:) = MHF_ind_swing;

            stride_time_sub_swing(v,:) = interp1(linspace(min(sample_vec),max(sample_vec),length(swing_ind)),stride_time_trial(:,swing_ind),sample_vec);
            

        end

        % Full Stride
        thigh_angle_task = [thigh_angle_task; thigh_angle_sub];
        knee_angle_task = [knee_angle_task; knee_angle_sub];
        ankle_angle_task = [ankle_angle_task; ankle_angle_sub];

        thigh_velocity_task = [thigh_velocity_task; thigh_velocity_sub];
        knee_velocity_task = [knee_velocity_task; knee_velocity_sub];
        ankle_velocity_task = [ankle_velocity_task; ankle_velocity_sub];

        stride_time_task = [stride_time_task; stride_time_sub];

        % Stance Stride
        thigh_angle_task_stance = [thigh_angle_task_stance; thigh_angle_sub_stance];
        knee_angle_task_stance = [knee_angle_task_stance; knee_angle_sub_stance];
        ankle_angle_task_stance = [ankle_angle_task_stance; ankle_angle_sub_stance];

        thigh_velocity_task_stance = [thigh_velocity_task_stance; thigh_velocity_sub_stance];
        knee_velocity_task_stance = [knee_velocity_task_stance; knee_velocity_sub_stance];
        ankle_velocity_task_stance = [ankle_velocity_task_stance; ankle_velocity_sub_stance];

        stride_time_task_stance = [stride_time_task_stance; stride_time_sub_stance];

        % Swing Stride
        thigh_angle_task_swing = [thigh_angle_task_swing; thigh_angle_sub_swing];
        knee_angle_task_swing = [knee_angle_task_swing; knee_angle_sub_swing];
        ankle_angle_task_swing = [ankle_angle_task_swing; ankle_angle_sub_swing];

        thigh_velocity_task_swing = [thigh_velocity_task_swing; thigh_velocity_sub_swing];
        knee_velocity_task_swing = [knee_velocity_task_swing; knee_velocity_sub_swing];
        ankle_velocity_task_swing = [ankle_velocity_task_swing; ankle_velocity_sub_swing];

        stride_time_task_swing = [stride_time_task_swing; stride_time_sub_swing];

    end

    vaf_task = [];
    for t = 1:size(thigh_angle_task_stance,1)
        vaf_task(t,:) = VAF(thigh_angle_task_stance(t,:),mean(thigh_angle_task_stance,'omitnan'));
    end

    vaf_ind = vaf_task > 75;
    %Full GC data
        % mean of trials
    dataOut.(task).full.thigh_angle_mean = mean(thigh_angle_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.knee_angle_mean = mean(knee_angle_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.ankle_angle_mean = mean(ankle_angle_task(vaf_ind,:),'omitnan');
    
    dataOut.(task).full.thigh_velocity_mean = mean(thigh_velocity_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.knee_velocity_mean = mean(knee_velocity_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.ankle_velocity_mean = mean(ankle_velocity_task(vaf_ind,:),'omitnan');
    
    dataOut.(task).full.stride_time_mean = mean(stride_time_task(vaf_ind,:),'omitnan');
        % std of trials
    dataOut.(task).full.thigh_angle_std = std(thigh_angle_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.knee_angle_std = std(knee_angle_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.ankle_angle_std = std(ankle_angle_task(vaf_ind,:),'omitnan');
    
    dataOut.(task).full.thigh_velocity_std = std(thigh_velocity_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.knee_velocity_std = std(knee_velocity_task(vaf_ind,:),'omitnan');
    dataOut.(task).full.ankle_velocity_std = std(ankle_velocity_task(vaf_ind,:),'omitnan');
    
    dataOut.(task).full.stride_time_std = std(stride_time_task(vaf_ind,:),'omitnan');
        % all trials
    dataOut.(task).full.thigh_angle = (thigh_angle_task(vaf_ind,:));
    dataOut.(task).full.knee_angle = (knee_angle_task(vaf_ind,:));
    dataOut.(task).full.ankle_angle = (ankle_angle_task(vaf_ind,:));
    
    dataOut.(task).full.thigh_velocity = (thigh_velocity_task(vaf_ind,:));
    dataOut.(task).full.knee_velocity = (knee_velocity_task(vaf_ind,:));
    dataOut.(task).full.ankle_velocity = (ankle_velocity_task(vaf_ind,:));

    dataOut.(task).full.stride_time = (stride_time_task(vaf_ind,:));


    %Stance GC data
        % mean of trials
    dataOut.(task).stance.thigh_angle_mean = mean(thigh_angle_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.knee_angle_mean = mean(knee_angle_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.ankle_angle_mean = mean(ankle_angle_task_stance(vaf_ind,:),'omitnan');
    
    dataOut.(task).stance.thigh_velocity_mean = mean(thigh_velocity_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.knee_velocity_mean = mean(knee_velocity_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.ankle_velocity_mean = mean(ankle_velocity_task_stance(vaf_ind,:),'omitnan');
    
    dataOut.(task).stance.stride_time_mean = mean(stride_time_task_stance(vaf_ind,:),'omitnan');
    
        % std of trials
    dataOut.(task).stance.thigh_angle_std = std(thigh_angle_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.knee_angle_std = std(knee_angle_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.ankle_angle_std = std(ankle_angle_task_stance(vaf_ind,:),'omitnan');
    
    dataOut.(task).stance.thigh_velocity_std = std(thigh_velocity_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.knee_velocity_std = std(knee_velocity_task_stance(vaf_ind,:),'omitnan');
    dataOut.(task).stance.ankle_velocity_std = std(ankle_velocity_task_stance(vaf_ind,:),'omitnan');
    
    dataOut.(task).stance.stride_time_std = std(stride_time_task_stance(vaf_ind,:),'omitnan');
    
        % all trials
    dataOut.(task).stance.thigh_angle = (thigh_angle_task_stance(vaf_ind,:));
    dataOut.(task).stance.knee_angle = (knee_angle_task_stance(vaf_ind,:));
    dataOut.(task).stance.ankle_angle = (ankle_angle_task_stance(vaf_ind,:));
    
    dataOut.(task).stance.thigh_velocity = (thigh_velocity_task_stance(vaf_ind,:));
    dataOut.(task).stance.knee_velocity = (knee_velocity_task_stance(vaf_ind,:));
    dataOut.(task).stance.ankle_velocity = (ankle_velocity_task_stance(vaf_ind,:));
    
    dataOut.(task).stance.stride_time = (stride_time_task_stance(vaf_ind,:));
    
    %Swing GC data
        % mean of trials
    dataOut.(task).swing.thigh_angle_mean = mean(thigh_angle_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.knee_angle_mean = mean(knee_angle_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.ankle_angle_mean = mean(ankle_angle_task_swing(vaf_ind,:),'omitnan');
    
    dataOut.(task).swing.thigh_velocity_mean = mean(thigh_velocity_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.knee_velocity_mean = mean(knee_velocity_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.ankle_velocity_mean = mean(ankle_velocity_task_swing(vaf_ind,:),'omitnan');
    
    dataOut.(task).swing.stride_time_mean = mean(stride_time_task_swing(vaf_ind,:),'omitnan');
    
        % std of trials
    dataOut.(task).swing.thigh_angle_std = std(thigh_angle_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.knee_angle_std = std(knee_angle_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.ankle_angle_std = std(ankle_angle_task_swing(vaf_ind,:),'omitnan');
    
    dataOut.(task).swing.thigh_velocity_std = std(thigh_velocity_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.knee_velocity_std = std(knee_velocity_task_swing(vaf_ind,:),'omitnan');
    dataOut.(task).swing.ankle_velocity_std = std(ankle_velocity_task_swing(vaf_ind,:),'omitnan');
    
    dataOut.(task).swing.stride_time_std = std(stride_time_task_swing(vaf_ind,:),'omitnan');
    
        % all trials
    dataOut.(task).swing.thigh_angle = (thigh_angle_task_swing(vaf_ind,:));
    dataOut.(task).swing.knee_angle = (knee_angle_task_swing(vaf_ind,:));
    dataOut.(task).swing.ankle_angle = (ankle_angle_task_swing(vaf_ind,:));
    
    dataOut.(task).swing.thigh_velocity = (thigh_velocity_task_swing(vaf_ind,:));
    dataOut.(task).swing.knee_velocity = (knee_velocity_task_swing(vaf_ind,:));
    dataOut.(task).swing.ankle_velocity = (ankle_velocity_task_swing(vaf_ind,:));

    dataOut.(task).swing.stride_time = (stride_time_task_swing(vaf_ind,:));
end

dataOut.segmentLengths.thigh = thigh_lengths;
dataOut.segmentLengths.shank = shank_lengths;

end