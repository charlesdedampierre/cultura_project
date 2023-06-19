library('ggplot2')
library(dplyr)
library(ggrepel)


plot_trends <- function(df_decade, region_name, min_time, max_time, span) {

  # Filter by region
  df_decade <- df_decade[which(df_decade$region_name == region_name), ]
  df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
  df_decade$cultural_score <- log(1 + df_decade$cultural_score)
  df_decade$cultural_score <- (df_decade$cultural_score - min(df_decade$cultural_score)) / (max(df_decade$cultural_score) - min(df_decade$cultural_score))

  y_axis <- "Log Normalized Cultural Index"
  name <- region_name

  myplot <- ggplot(df_decade, aes(x = decade, y = cultural_score, color = region_name)) +
    geom_line(alpha = 0.3, linewidth = 0.5, colour = 'darkblue') +
    geom_smooth(method = 'loess', span = span, level = 0.95, linewidth = 1.5, colour = 'darkblue') +
    scale_x_continuous(breaks = seq(floor(min_time/100) * 100, floor(max_time/100) * 100, 100)) +
    theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
    theme(plot.title = element_text(hjust = 0.5)) +
    ggtitle(name) +
    xlab("") +
    scale_y_continuous(name = y_axis) +
    guides(color = guide_legend('region_name')) +
    scale_color_hue(direction = 1, h.start = 180) +
    theme(legend.position = "none") +
    theme_classic()

  return(myplot)
}

