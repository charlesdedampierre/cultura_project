source("r_visual_scripts/functions.R")

df_decade <- read.csv(file = "data/df_trends_works.csv", sep = ",", header = TRUE)
df_decade <- read.csv(file = "data/df_trends_individuals.csv", sep = ",", header = TRUE)

plot_trend = plot_trends(df_decade, "Chinese world", -500, 1800, 0.2)
ggsave('test.png', plot = plot_trend, dpi = 600,  width = 10, height = 8)