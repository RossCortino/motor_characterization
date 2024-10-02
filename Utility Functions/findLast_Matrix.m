function V = findLast_Matrix(A)
V = zeros(size(A,1),1);
for ix = 1:size(A,1)
    indx = find(A(ix,:),1,'last');
    if isempty(indx)
        V(ix) = NaN;
    else
        V(ix) = indx;
    end
end
end