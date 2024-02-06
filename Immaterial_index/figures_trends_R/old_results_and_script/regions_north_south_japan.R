source("index_duo.R")

span <- 0.4
min_date <- 700
max_date <- 1800
log <- "True"

df_decade <- read.csv(file = "../results/df_region_score.csv", sep = ",", header = TRUE)

# Group by decades and sum the scores
df_decade <- df_decade %>%
  mutate(decade = floor(decade / 50) * 50) %>%
  group_by(region_name, decade) %>%
  summarise(score = sum(score))


region_1 <- "Southern Japan"
region_2 <- "Northern Japan"

name <- "Eastern and Western Japan"

df_decade <- filter(df_decade, region_name == region_1 | region_name == region_2)


df_indi <- read.csv(file = "../results/df_individuals_score.csv", sep = ",", header = TRUE)
df_indi <- filter(df_indi, region_name == region_1 | region_name == region_2)

df_decade$score <- log(df_decade$score)

plot_trend <- plot_trends_duo(df_decade, df_indi, min_date, max_date, span, log, name)
ggsave("results/japan_north_south.png", plot = plot_trend, dpi = 300, width = 10, height = 8)
