clearvars -except Normalized GT_Dataset_Corrected called



    % Laptop
    addpath("C:\Users\rcort\Documents\Research\Datasets\")
    % Home
    addpath("D:\Desktop\Research\Datasets\")
    addpath("C:\Users\cortinrj\Documents\Datasets\")




if ~exist("Normalized")
    load("Normalized.mat")
end

dataset = Normalized;


%Params
stride = "s3";
activity = "Stair";
stairData = getStrideBiomechanics_R01(dataset,activity,stride);