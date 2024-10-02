function [h] = plotShadedCurve(ax,mainCurve,boundsCurve, color, x, linestyle, legendVis, lineWidth)
if ~exist('color','var')
    color = [0,0,1];
end
if ~exist('x','var')
    x = 0:length(mainCurve)-1;
end
if ~exist('linestyle','var')
    linestyle = '-';
end
if ~exist('legendVis','var')
    legendVis = 'on';
end
if ~exist('lineWidth','var')
    lineWidth = 1;
end
if size(mainCurve,1) == 1
    mainCurve = mainCurve';
end
if size(boundsCurve, 1) == 1
    boundsCurve = boundsCurve';
end
if size(x, 1) == 1
    x = x';
end

curve1 =  mainCurve + boundsCurve;
curve2 = mainCurve - boundsCurve;
hold(ax,'on')
fill(ax,[x;flipud(x)],[curve1; flipud(curve2)],color,'HandleVisibility','off','facealpha',.2,'EdgeAlpha',0)
h = plot(ax,x,mainCurve, 'color', color, 'LineStyle', linestyle, 'HandleVisibility',legendVis, 'LineWidth',lineWidth);

end