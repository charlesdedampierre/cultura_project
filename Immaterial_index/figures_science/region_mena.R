source("index_global.R")

region_name <- "Muslim world"
name <- "Middle-East and North-Africa"
log <- "True"
span <- 0.3
min_date <- -600
max_date <- 1800
df_decade <- read.csv(file = "../../results/df_region_score_science.csv", sep = ",", header = TRUE)

# Group by decades and sum the scores
df_decade <- df_decade %>%
    mutate(decade = floor(decade / 50) * 50) %>%
    group_by(region_name, decade) %>%
    summarise(score = sum(score))



df_indi <- read.csv(file = "../../results/df_individuals_score_science.csv", sep = ",", header = TRUE)

# df_indi$score <- log(df_indi$score + 1)
df_decade$score <- log(df_decade$score)

# text size is at 10
plot_trend <- plot_trends(df_decade, df_indi, region_name, min_date, max_date, span, log, name, time_size = 8)
ggsave("results/mena.png", plot = plot_trend, dpi = 300, width = 10, height = 8)
