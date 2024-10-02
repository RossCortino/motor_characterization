function outVal = calcPoly(coeffs, x)
% Calculates a polynomial evaluated at x where coeffs is an ordered vector
% of coefficeints. Eg. coeffs(1) + coeffs(2)*x + .... coeffs(n)*x^(n-1); 
outVal = 0;
for ix = 1:length(coeffs)
    outVal = outVal + coeffs(ix) * ( x.^(ix-1));
end
end