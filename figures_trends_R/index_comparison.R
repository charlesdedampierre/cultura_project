library("ggplot2")
library(dplyr)
library(ggrepel)

plot_trends <- function(df_decade, df_indi, min_time, max_time, span) {
  # df_indi <- df_indi[which(df_indi$region_name == region_name), ]
  df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]
  # df_indi$score <- log(1 + df_indi$score)
  df_indi$score <- (df_indi$score - min(df_indi$score)) / (max(df_indi$score) - min(df_indi$score))

  # Filter by region
  # df_decade <- df_decade[which(df_decade$region_name == region_name), ]
  df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
  # df_decade$score <- log(1 + df_decade$score)
  df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))

  y_axis <- "Log Immaterial Index"
  y_axis_2 <- "Individual Immaterial Index"

  myplot <- ggplot(df_decade, aes(x = decade, y = score, color = region_name)) +
    # geom_line(alpha = 0.3, linewidth = 0.5) +
    # geom_bar(stat = "identity", fill = "lightgrey", alpha = 0.7, color = "lightgrey", ) +
    geom_smooth(method = "loess", span = span, level = 0.3, linewidth = 1.5) +
    scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
    theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
    theme(plot.title = element_text(hjust = 0.5)) +
    ggtitle("") +
    xlab("") +
    # scale_y_continuous(name = y_axis) +
    scale_y_continuous(name = y_axis, sec.axis = sec_axis(trans = ~ . * 1, name = y_axis_2)) +
    guides(color = guide_legend("region_name")) +
    scale_color_hue(direction = 1, h.start = 180) +
    theme(legend.position = "none") +
    geom_point(data = df_indi, aes(x = decade, y = score), alpha = 0.2, size = 0.5) +
    geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 60), aes(x = decade, y = score, label = individual_name), size = 3, alpha = 5, max.overlaps = 50) +
    theme_classic()

  return(myplot)
}

span <- 0.4
min_date <- -800
max_date <- 500

df_decade <- read.csv(file = "../data/df_region_score.csv", sep = ",", header = TRUE)

# Group by decades and sum the scores
df_decade <- df_decade %>%
  mutate(decade = floor(decade / 50) * 50) %>%
  group_by(region_name, decade) %>%
  summarise(score = sum(score))


region_1 <- "Greek World"
region_2 <- "Italy"

df_decade <- filter(df_decade, region_name == region_1 | region_name == region_2)


df_indi <- read.csv(file = "../data/df_individuals_score.csv", sep = ",", header = TRUE)
df_indi <- filter(df_indi, region_name == region_1 | region_name == region_2)


plot_trend <- plot_trends(df_decade, df_indi, min_date, max_date, span)
ggsave("test.png", plot = plot_trend, dpi = 300, width = 10, height = 8)
