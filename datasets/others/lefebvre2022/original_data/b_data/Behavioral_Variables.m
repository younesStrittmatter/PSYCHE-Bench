%% This script compute and plot behavioural variable of interest.
clear all
close all

%% Population definition
exp=input('Experiment?(1 or 2)'); % 1: experiment 1 (reward and reward omission) / 2: experiment 2 (reward and punishment)

%% Data Extraction

if exp==1;
    subjects=1:50; % 50 subjects from experiments 1
    cd data_exp1/
elseif exp==2;
    subjects=1:35; % 35 subjects from experiments 2
    cd data_exp2/
end

for i = subjects;
    
    if exp==1;
        
        load(strcat('exp1_',num2str(i)));
        
        con{i}  = data(:,3);                    % 1 to 4 as per condition
        cho{i}  = data(:,7)/2+1.5;              % 1 for left, 2 for right
        out{i}  = data(:,8)/2;                  % 0 or 0.5 euros
               
    elseif exp==2;
       
        load(strcat('exp2_',num2str(i)));
        
        con{i}  = data(:,3);                 % 1 to 4 as per condition
        cho{i}  = data(:,5)/2+1.5;           % 1 for left, 2 for right
        out{i}  = data(:,8);                 % -0.5 or 0.5 euros
                
    end

end

cd ..

%% Behavioral Variable Construction
hyperCho=vector_to_structure_matrix(cho,1,96);
hyperCon=vector_to_structure_matrix(con,1,96);

choice1=structure_matrix_to_plotmatrix(hyperCho,1,hyperCon,numel(subjects),1,24,-1);
choice2=structure_matrix_to_plotmatrix(hyperCho,2,hyperCon,numel(subjects),1,24,-1);
choice3=structure_matrix_to_plotmatrix(hyperCho,3,hyperCon,numel(subjects),1,24,-1);
choice4=structure_matrix_to_plotmatrix(hyperCho,4,hyperCon,numel(subjects),1,24,-1);

%% Graph

% Color Definition
Colors(1,:)=[0.5 0 0];
Colors(2,:)=[0.5 0 0];
Colors(3,:)=[0.5 0 0];
Colors(4,:)=[0.5 0 0];

% Bar Plot

figure;

subplot(2,2,1); % Right
meandata=nan(4,numel(choice1(1,:)));
meandata(1,:)=mean(choice1);
meandata(2,:)=mean(choice2);
meandata(3,:)=mean(choice3);
meandata(4,:)=mean(choice4);
PlotFunction(meandata,Colors,0,1,14);
title('right')
ylabel('Arbitrary units')

subplot(2,2,2); % Correct
meandata2=zeros(4,numel(choice1(1,:)));
meandata2(2,:)=mean(1-choice2);
meandata2(3,:)=mean(choice3);
PlotFunction(meandata2,Colors,0,1,14);
title('Correct')

subplot(2,4,5);
PlotFunction2((choice1),[0.25 0.5 0.75],[0.5 0 0],1,0.5,0,1,10,'25/25','Trials','P(right)');
subplot(2,4,6);
PlotFunction2((choice2),[0.25 0.5 0.75],[0.5 0 0],1,0.5,0,1,10,'75/25','Trials','P(right)');
subplot(2,4,7);
PlotFunction2((choice3),[0.25 0.5 0.75],[0.5 0 0],1,0.5,0,1,10,'25/75','Trials','P(right)');
subplot(2,4,8);
PlotFunction2((choice4),[0.25 0.5 0.75],[0.5 0 0],1,0.5,0,1,10,'75/75','Trials','P(right)');










