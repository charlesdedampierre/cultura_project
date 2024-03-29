library("ggplot2")
library(dplyr)
library(ggrepel)

plot_trends <- function(df_decade, df_indi, region_name, min_time, max_time, capita = FALSE, name, time_size = 15) {
    df_indi <- df_indi[which(df_indi$region_name == region_name), ]
    df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]
    # Group by decades and sum the scores
    df_decade <- df_decade %>%
        mutate(decade = floor(decade / 50) * 50) %>%
        group_by(region_name, decade) %>%
        summarise(score = sum(score))

    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
    df_decade$score <- log(df_decade$score)
    df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))


    y_axis <- ifelse(capita,
        "Log Immaterial Index (number of individuals) per capita",
        "Immaterial Index (number of individuals)"
    )

    y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"



    color <- "#00bfc4"
    color <- "#f8766d"

    coeff_y_axis <- max(df_indi$score) / max(df_decade$score)
    myplot <- ggplot(df_decade, aes(x = decade, y = score, color = region_name)) +
        geom_line(alpha = 0.3, linewidth = 0.5, colour = "darkblue") +
        # geom_bar(stat = "identity", color = "transparent", alpha = 0.2, fill = "blue") +
        geom_smooth(method = "loess", span = span, level = 0, linewidth = 1.5, colour = "darkblue") +
        scale_x_continuous(breaks = seq(500, 1800, by = 500)) +
        # scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        ggtitle(name) +
        xlab("") +
        scale_y_continuous(name = y_axis, sec.axis = sec_axis(trans = ~ . * coeff_y_axis, name = y_axis_2)) +
        guides(color = guide_legend("region_name")) +
        scale_color_hue(direction = 1, h.start = 180) +
        theme(legend.position = "none") +
        geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
        geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 30), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
        theme_classic() +
        theme(plot.title = element_text(hjust = 0.5, size = 35)) +
        theme(legend.position = "none") +
        theme(axis.text.x = element_text(size = 30)) +
        theme(axis.text.y = element_text(size = 30)) +
        theme(
            axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
        )


    return(myplot)
}


region_name <- "United Kingdom"
name <- region_name
span <- 0.3
log <- "True"
min_date <- 500
max_date <- 1800

df_decade <- read.csv(file = "../results/df_region_score.csv", sep = ",", header = TRUE)
df_indi <- read.csv(file = "../results/df_individuals_score.csv", sep = ",", header = TRUE)

plot_trend <- plot_trends(df_decade, df_indi, region_name, min_date, max_date, capita = FALSE, name, time_size = 8)
ggsave("results/United Kingdom.png", plot = plot_trend, dpi = 300, width = 10, height = 8)

df_population <- read.csv("../../environnement_data/population_region_name.csv")
df_population <- df_population %>%
    rename(decade = year)

# Merge df_decade_poulation with df_population on the "region_name" column
df_decade_poulation <- inner_join(df_decade, df_population, by = c("region_name", "decade"))
df_decade_poulation <- df_decade_poulation %>%
    mutate(score = score / population)

plot_trend_population <- plot_trends(df_decade_poulation, df_indi, region_name, min_date, max_date, capita = TRUE, name, time_size = 8)
ggsave("results_per_capita/United Kingdom.png", plot = plot_trend_population, dpi = 300, width = 10, height = 8)
