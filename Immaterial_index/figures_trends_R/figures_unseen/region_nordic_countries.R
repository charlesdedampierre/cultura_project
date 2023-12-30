library("ggplot2")
library(dplyr)
library(ggrepel)

scale_column <- function(data_frame, column_name) {
    min_val <- min(data_frame[[column_name]])
    max_val <- max(data_frame[[column_name]])
    data_frame[[column_name]] <- (data_frame[[column_name]] - min_val) / (max_val - min_val)
    return(data_frame)
}

plot_trends <- function(df_decade, df_indi, region_name, min_time, max_time, span, name, capita = "True", time_size = 15, text_position = 5) {
    df_indi <- df_indi[which(df_indi$region_name == region_name), ]
    df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]

    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]

    # Scaling
    # df_decade <- scale_column(df_decade, "score")
    # df_decade <- scale_column(df_decade, "lower")
    # df_decade <- scale_column(df_decade, "upper")
    # df_indi <- scale_column(df_indi, "score")

    # Conditional statement
    if (capita == "True") {
        # Code to execute if log is TRUE
        y_axis <- "Log10 Immaterial Index (corrected number of individuals) per capita"
        y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"
    } else {
        y_axis <- "Log10 Immaterial Index (corrected number of individuals)"
        y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"
    }

    color <- "#00bfc4"
    color <- "#f8766d"


    min_value_left_axis <- min(df_decade$score, na.rm = TRUE)
    min_value_right_axis <- min(df_indi$score, na.rm = TRUE)

    coeff_y_axis <- max(df_indi$score) / max(df_decade$lower)

    myplot <- ggplot(df_decade, aes(x = decade, y = score, color = region_name)) +
        # geom_ribbon(data = df_decade, aes(x = decade, ymin = lower, ymax = upper), fill = "grey80", color = "lightblue") +

        geom_ribbon(data = df_decade, aes(x = decade, ymin = predict(loess(lower ~ decade, span = span)), ymax = predict(loess(upper ~ decade, span = span))), fill = "grey80", color = "lightblue") +
        geom_smooth(method = "loess", span = span, se = FALSE, , linewidth = 1.5, colour = "darkblue") +

        # geom_ribbon(data = df_decade, aes(x = decade, ymin = lower, ymax = upper), fill = "grey80", color = "lightblue") +
        # geom_line(aes(x = decade, y = score), size = 1, color = "darkblue") + # Add the line for "score"
        # geom_bar(stat = "identity", color = "transparent", alpha = 0.2, fill = "blue") +
        scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        theme(plot.title = element_text(hjust = 0.5)) +
        ggtitle(name) +
        xlab("") +
        scale_y_continuous(
            name = y_axis,
            limits = c(min_value_left_axis, NA), # Set the minimum for the left y-axis
            sec.axis = sec_axis(~ . * coeff_y_axis + (min_value_right_axis - min_value_left_axis * coeff_y_axis),
                name = y_axis_2
            )
        ) + # Adjust the right y-axis +
        guides(color = guide_legend("region_name")) +
        scale_color_hue(direction = 1, h.start = 180) +
        theme(legend.position = "none") +
        geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
        geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 30), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
        theme_classic() +
        theme(plot.title = element_text(hjust = 0.5)) +
        theme(legend.position = "none") +
        theme(axis.text.x = element_text(size = time_size)) +
        theme(axis.text.y = element_text(size = 15)) +
        theme(
            axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
        )
    return(myplot)
}

region_name <- "Nordic countries"
name <- region_name
log <- "True"
span <- 0.2
min_date <- 500
max_date <- 1800
min_individuals_per_century <- 0


df_score <- read.csv(file = "../../results/df_region_score.csv", sep = ",", header = TRUE)
df_score <- df_score %>%
    rename(count_individuals = score)
df_score <- df_score[which(df_score$region_name == region_name), ]
df_score <- df_score[(df_score$decade >= min_date) & (df_score$decade <= max_date), ]

# Create a new column for the century
df_score <- df_score %>%
    mutate(century = ceiling(decade / 100) * 100)


# Group by century and summarize the data
result <- df_score %>%
    group_by(century) %>%
    summarize(total_individuals = sum(count_individuals))

print(result)

# Group by century and summarize the data
result <- df_score %>%
    group_by(century) %>%
    summarize(total_individuals = sum(count_individuals)) %>%
    filter(total_individuals > min_individuals_per_century)

# Filter the original data based on the selected centuries
df_score <- df_score %>%
    filter(century %in% result$century)

df_indi <- read.csv(file = "../../results/df_individuals_score.csv", sep = ",", header = TRUE)
df_unseen <- read.csv(file = "../../../unseen_species_model/results/estimations.csv", sep = ",", header = TRUE)
# Rename columns
df_unseen <- df_unseen %>%
    rename(score = N_est, region_name = region, lower = lower, upper = upper)


# Filter by the min number of individuals per century
df_indi <- df_indi %>%
    mutate(century = ceiling(productive_year / 100) * 100)

df_unseen <- df_unseen %>%
    mutate(century = ceiling(decade / 100) * 100)

df_unseen <- df_unseen %>%
    filter(century %in% result$century)

df_indi <- df_indi %>%
    filter(century %in% result$century)

df_unseen$score <- log10(df_unseen$score)
df_unseen$lower <- log10(df_unseen$lower)
df_unseen$upper <- log10(df_unseen$upper)

plot_trend_unseen <- plot_trends(df_unseen, df_indi, region_name, min_date, max_date, span = span, name = name, capita = "True", time_size = 8, text_position = 2)
ggsave("results_unseen/nordic_countries.png", plot = plot_trend_unseen, dpi = 300, width = 10, height = 8)

df_unseen <- read.csv(file = "../../../unseen_species_model/results/estimations.csv", sep = ",", header = TRUE)
# Rename columns
df_unseen <- df_unseen %>%
    rename(score = N_est, region_name = region, lower = lower, upper = upper)

df_unseen <- df_unseen %>%
    mutate(century = ceiling(decade / 100) * 100)

df_unseen <- df_unseen %>%
    filter(century %in% result$century)

df_population <- read.csv(file = "../../../environnement_data/population_region_name.csv", sep = ",", header = TRUE)
df_population <- df_population %>%
    rename(decade = year)

df_unseen <- merge(df_unseen, df_population, by = c("decade", "region_name"))
df_unseen$score <- df_unseen$score / df_unseen$population
df_unseen$lower <- df_unseen$lower / df_unseen$population
df_unseen$upper <- df_unseen$upper / df_unseen$population

df_unseen$score <- log10(df_unseen$score)
df_unseen$lower <- log10(df_unseen$lower)
df_unseen$upper <- log10(df_unseen$upper)

# Check if the minimum lower value is less than zero
min_lower <- min(df_unseen$lower, na.rm = TRUE)
if (min_lower < 0) {
    # Add the absolute value of the minimum lower value to all lower values
    df_unseen$lower <- df_unseen$lower + abs(min_lower)
    # Since we are adjusting the lower values, we need to apply the same adjustment to the upper values and score
    df_unseen$upper <- df_unseen$upper + abs(min_lower)
    df_unseen$score <- df_unseen$score + abs(min_lower)
}

# cmd + option + /

plot_trend_unseen <- plot_trends(df_unseen, df_indi, region_name, min_date, max_date, span = span, name, capita = "True", time_size = 15, text_position = 2.15)
ggsave("results_unseen/per_capita/nordic_countries.png", plot = plot_trend_unseen, dpi = 300, width = 10, height = 8)
