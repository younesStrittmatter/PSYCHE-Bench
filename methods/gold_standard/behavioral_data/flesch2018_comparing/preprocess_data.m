%%% This script is just to convert the data provided by the authors from
%%% matlab format (.mat) into csv format.

clear all;
% load data from experiment 1a
data = load("original_data/rsData_exp1a.mat");

all_data1 = table;
counter=0;
for i=1:length(data.rsData)
    all_data1.participant((1+600*counter):(1+600*counter+599))=i-1;
    all_data1.task((1+600*counter):(1+600*counter+599)) = int32(0);
    all_data1.trial((1+600*counter):(1+600*counter+599)) = linspace(0,599 ,600)';
    all_data1.block((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,1)-1;
    all_data1.session((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,2)-1;
    all_data1.choice((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,8);
    all_data1.reward((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,7);
    all_data1.context((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,3)-1;
    all_data1.leaf((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,4)-1;
    all_data1.branch((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,5)-1;
    all_data1.cat((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,6);
    counter=counter+1;
end 
% write data from experiment 1a
%writetable(all_data1,'/Users/vuongtruong/Desktop/CENTaUR/CENTaUR2/Flesch2018Comparing/exp1a.csv','Delimiter',',')  

clear data;
% load data from experiment 1b
data = load("original_data/rsData_exp1b.mat");

all_data2 = table;
counter=0;
for i=1:length(data.rsData)
    all_data2.participant((1+600*counter):(1+600*counter+599))=i+175;
    all_data2.task((1+600*counter):(1+600*counter+599)) = int32(0);
    all_data2.trial((1+600*counter):(1+600*counter+599)) = linspace(0,599 ,600)';
    all_data2.block((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,1)-1;
    all_data2.session((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,2)-1;
    all_data2.choice((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,8);
    all_data2.reward((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,7);
    all_data2.context((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,3)-1;
    all_data2.leaf((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,4)-1;
    all_data2.branch((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,5)-1;
    all_data2.cat((1+600*counter):(1+600*counter+599)) = data.rsData(i).data(:,6);
    counter=counter+1;
end 
% combine the data from two experiments
combined_data = vertcat(all_data1, all_data2);
% write the data into a csv file 
writetable(combined_data,'exp1.csv','Delimiter',',')