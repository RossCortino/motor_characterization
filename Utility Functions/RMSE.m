function RMSEout = RMSE(y, yhat)
    RMSEout = sqrt(sum((y - yhat).^2)/length(y));
end
