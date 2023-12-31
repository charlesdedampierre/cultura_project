source("index_global.R")

region_name <- "United Kingdom"
name <- region_name
span <- 0.3
log <- "True"
min_date <- 500
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


plot_trend <- plot_trends(df_decade, df_indi, region_name, min_date, max_date, span, log, name)
ggsave("results/united_kingdom.png", plot = plot_trend, dpi = 300, width = 10, height = 8)
