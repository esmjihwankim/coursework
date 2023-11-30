figure(1), elf 
subplot(131)
bar(1:n,mean(data))
axis square, set(gca, 'xlim', [0 n+1], 'xtick'