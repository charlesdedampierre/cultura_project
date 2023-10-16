library("ggplot2")
library(dplyr)
library(ggrepel)

plot_trends <- function(df_decade, df_indi, region_name, min_time, max_time, span) {
  df_indi <- df_indi[which(df_indi$region_name == region_name), ]
  df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]
  # df_indi$score <- log(1 + df_indi$score)
  # df_indi$score <- (df_indi$score - min(df_indi$score)) / (max(df_indi$score) - min(df_indi$score))

  # Filter by region
  df_decade <- df_decade[which(df_decade$region_name == region_name), ]
  df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
  # df_decade$score <- log(1 + df_decade$score)
  # df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))

  y_axis <- "Immaterial Index (number of individuals)"
  y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"
  name <- region_name

  color <- "#00bfc4"


  coeff_y_axis <- max(df_indi$score) / max(df_decade$score)
  myplot <- ggplot(df_decade, aes(x = decade, y = score, color = region_name)) +
    # geom_line(alpha = 0.3, linewidth = 0.5, colour = "darkblue") +
    geom_bar(stat = "identity", color = "transparent", alpha = 0.2, fill = color) +
    geom_smooth(method = "loess", span = span, level = 0, linewidth = 1.5, colour = color) +
    scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
    theme(
      panel.border = element_blank(),
      panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
      axis.line = element_line(
        colour = "grey"
      )
    ) +
    theme(plot.title = element_text(hjust = 0.5)) +
    # ggtitle(name) +
    xlab("") +
    scale_y_continuous(name = y_axis, sec.axis = sec_axis(trans = ~ . * coeff_y_axis, name = y_axis_2)) +
    guides(color = guide_legend("region_name")) +
    scale_color_hue(direction = 1, h.start = 180) +
    theme(legend.position = "none") +
    geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
    geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 30), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
    theme_classic() +
    theme(legend.position = "none") +
    theme(axis.text.x = element_text(size = 15)) +
    theme(axis.text.y = element_text(size = 15)) +
    theme(
      axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
    ) +

    # Augustin: 43 bc to ad 18
    # Nerva–Antonine dynasty: 96 to 192
    # Severan\n dynasty: 193-235
    # Third century\n (Military Anarchy): 235-284
    # constantitian : 305-363

    geom_vline(xintercept = c(-800, -480), linetype = "dashed", color = "grey80") +
    geom_vline(xintercept = c(-480, -323), linetype = "dashed", color = "grey80") +
    geom_vline(xintercept = c(-323, -31), linetype = "dashed", color = "grey80") +
    geom_vline(xintercept = c(-31, 500), linetype = "dashed", color = "grey80") +
    geom_text(aes(x = -640, y = 100, size = 7), label = "Archaic Period", color = "grey80", angle = 90, vjust = 0.5, hjust = 0) +
    geom_text(aes(x = -401.5, y = 100, size = 7), label = "Classical Period ", color = "grey80", angle = 90, vjust = 0.5, hjust = 0) +
    geom_text(aes(x = -177, y = 100, size = 7), label = "Hellenistic Period", color = "grey80", angle = 90, vjust = 0.5, hjust = 0) +
    geom_text(aes(x = 234.5, y = 100, size = 7), label = "Roman Greece", color = "grey80", angle = 90, vjust = 0.5, hjust = 0)
  return(myplot)
}


region_name <- "Greek World"
span <- 0.4
min_date <- -800
max_date <- 500
df_decade <- read.csv(file = "../../data/df_region_score.csv", sep = ",", header = TRUE)

# Group by decades and sum the scores
df_decade <- df_decade %>%
  mutate(decade = floor(decade / 50) * 50) %>%
  group_by(region_name, decade) %>%
  summarise(score = sum(score))


df_indi <- read.csv(file = "../../data/df_individuals_score.csv", sep = ",", header = TRUE)



plot_trend <- plot_trends(df_decade, df_indi, region_name, min_date, max_date, span)
ggsave("greek.png", plot = plot_trend, dpi = 300, width = 10, height = 8)
