alldata <- read.table('t1II_stim.txt', header=F)

names(alldata) <- c('cat', 'cat2', 'length', 'orient')

plot(alldata$length, alldata$orient)