function [curve sem] = PlotFunction2(DataMatrix,Chance,Color,Line,Alpha,Yinf,Ysup,Font,Title,LabelX,LabelY)

[Ntrial Nsub]=size(DataMatrix);

curve= nanmean(DataMatrix,2);
sem  = nanstd(DataMatrix')'/sqrt(Nsub);

curveSup = (curve+sem);
curveInf = (curve-sem);

for n=1:Ntrial;
    chance(n,1)=Chance(1);
    chance(n,2)=Chance(2);
    chance(n,3)=Chance(3);
end
plot(curve+sem,...
    'Color',Color,...
    'LineWidth',Line);
hold on
plot(curve-sem,...
    'Color',Color,...
    'LineWidth',Line);
hold on
plot(curve,'B',...
    'Color',Color,...
    'LineWidth',Line*2);
hold on
fill([1:Ntrial flipud([1:Ntrial]')'],[curveSup' flipud(curveInf)'],'k',...
    'LineWidth',1,...
    'LineStyle','none',...
    'FaceColor',Color,...
    'FaceAlpha',Alpha);
plot(chance,'k',...
   'LineWidth',Line/2);
axis([0 Ntrial+1 Yinf Ysup]);
set(gca,'Fontsize',Font);
title(Title);
xlabel(LabelX);
ylabel(LabelY);
box ON