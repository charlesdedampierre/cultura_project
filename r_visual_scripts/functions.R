library('ggplot2')
library(dplyr)
library(ggrepel)


plot_trends <- function(df_decade, df_indi, region_name, min_time, max_time, span) {

  df_indi = df_indi[ which(df_indi$region_name==region_name),]
  df_indi =  df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time),]
  df_indi$cultural_score = log(1 + df_indi$cultural_score)
  df_indi$cultural_score = (df_indi$cultural_score-min(df_indi$cultural_score))/(max(df_indi$cultural_score)-min(df_indi$cultural_score))

  # Filter by region
  df_decade <- df_decade[which(df_decade$region_name == region_name), ]
  df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
  df_decade$cultural_score <- log(1 + df_decade$cultural_score)
  df_decade$cultural_score <- (df_decade$cultural_score - min(df_decade$cultural_score)) / (max(df_decade$cultural_score) - min(df_decade$cultural_score))

  y_axis <- "Log Normalized Cultural Index"
  y_axis_2 = "Log Normalized Individual Cultural Index"
  name <- region_name

  myplot <- ggplot(df_decade, aes(x = decade, y = cultural_score, color = region_name)) +
    geom_line(alpha = 0.3, linewidth = 0.5, colour = 'darkblue') +
    geom_smooth(method = 'loess', span = span, level = 0.95, linewidth = 1.5, colour = 'darkblue') +
    scale_x_continuous(breaks = seq(floor(min_time/100) * 100, floor(max_time/100) * 100, 100)) +
    theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
    theme(plot.title = element_text(hjust = 0.5)) +
    ggtitle(name) +
    xlab("") +
    #scale_y_continuous(name = y_axis) +
    scale_y_continuous(name = y_axis, sec.axis = sec_axis( trans=~.*1, name=y_axis_2)) +
    guides(color = guide_legend('region_name')) +
    scale_color_hue(direction = 1, h.start = 180) +
    theme(legend.position = "none") +

    geom_point(data=df_indi, aes(x=decade, y=cultural_score), alpha = 0.2, size = 0.5, colour = 'red') +
    geom_text_repel(data = head(df_indi[order(-df_indi$cultural_score),], 30), aes(x=decade, y=cultural_score, label = individual_name),  size = 3,  alpha = 5, max.overlaps = 50, color = 'red') +
    theme_classic()

  return(myplot)
}

