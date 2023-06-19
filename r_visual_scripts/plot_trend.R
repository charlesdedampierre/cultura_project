source("r_visual_scripts/functions.R")

region_name = 'Spain'
min_date = 1200
max_date = 1800

#df_decade <- read.csv(file = "data/df_trends_individuals.csv", sep = ",", header = TRUE)

df_decade <- read.csv(file = "data/df_trends_works.csv", sep = ",", header = TRUE)
df_indi <- read.csv(file = "data/df_indi_works.csv", sep = ",", header = TRUE)

plot_trend = plot_trends(df_decade, df_indi, region_name, min_date, max_date, 0.2)
ggsave('test.png', plot = plot_trend, dpi = 600,  width = 10, height = 8)