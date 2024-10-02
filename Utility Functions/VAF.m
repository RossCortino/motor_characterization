function VAFout = VAF(y, yhat)
% Calculate the Variance Accounted For. Y is true data, Yhat is model
% [1] M. M. Mirbagheri, H. Barbeau, and R. E. Kearney, “Intrinsic and reflex contributions to human ankle stiffness: Variation with activation level and position,” Exp. Brain Res., vol. 135, no. 4, pp. 423–436, 2000, doi: 10.1007/s002210000534.
VAFout = (1 - (sum((y-yhat).^2)/sum(y.^2))) * 100;
end