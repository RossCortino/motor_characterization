function MAEout = MAE(y, yhat)
MAEout = sum(abs(y-yhat))/length(y); 
end