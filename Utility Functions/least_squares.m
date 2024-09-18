function x = least_squares (A,b)


if size(A,1) == size(A,2) % Square
    x = inv(A)*b;
elseif size(A,1) < size(A,2) % Underdetermined (A is fat)
    x = A'*inv(A*A')*b;
else
    x = inv(A'*A)*A'*b; %Overdetermined (A is tall)
end
