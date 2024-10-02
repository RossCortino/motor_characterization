function output = maxMag(val)
    [valMax,valIndex] = max(abs(val));
    output = NaN(1,length(valMax));
    for i = 1:length(valMax)
        if ~isequal(size(valIndex),[1 1])
            output(i) = valMax(i).*sign(val(valIndex(i),i));
        else
            output(i) = valMax(i).*sign(val(valIndex(i)));
        end
    end
end