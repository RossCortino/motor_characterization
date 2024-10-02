%% Clamp function - verfied
function [y, limitActive] = clamp(x, x1, x2)
% Clamps x between the two limits
y = min(x,max(x1,x2));
y = max(y,min(x1,x2));

% Set flag if x was modified
limitActive = y ~= x;
end
