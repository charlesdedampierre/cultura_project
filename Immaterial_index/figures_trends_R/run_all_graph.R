# This script created all the Index graph (Global, per capita and the unseen species results). The script automamatically normalizes the y axis from
# 0 to 1 and log10 the results.
# All parameters are in the parameters_regions.json

library("ggplot2")
library(dplyr)
library(ggrepel)
library(jsonlite)

# plot_unseen_index <- function() {}



plot_cultural_index <- function(df_decade, df_indi, region_name, min_time, max_time, graph_type = "global", name, time_size = 15, x_intercepts, labels) {
    df_indi <- df_indi[which(df_indi$region_name == region_name), ]
    df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]

    # # Group by decades and sum the scores
    # df_decade <- df_decade %>%
    #     mutate(decade = floor(decade / 50) * 50) %>%
    #     group_by(region_name, decade) %>%
    #     summarise(score = sum(score))

    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]
    df_decade$score <- log10(df_decade$score)
    df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))

    # Check the value of graph_type and assign labels accordingly
    if (graph_type == "capita") {
        y_axis <- "Log Cultural Index per capita"
    } else if (graph_type == "global") {
        y_axis <- "Log Cultural Index"
    } else if (graph_type == "complexity") {
        y_axis <- "Log Complexity Index"
    } else {
        # Handle unexpected or missing values of graph_type
        cat("Unknown graph_type:", graph_type)
    }



    y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"


    color <- "#00bfc4"
    color <- "#f8766d"


    vline_geoms <- NULL
    text_geoms <- NULL

    tryCatch(
        {
            y_range <- range(df_decade$score)
            # Parameters for region on the plot
            text_position <- y_range[1] + 4 / 5 * diff(y_range)

            # Create a list of geom_vline objects
            vline_geoms <- lapply(x_intercepts, function(x) {
                geom_vline(xintercept = x, linetype = "dashed", color = "grey80")
            })

            # Calculate the midpoint of each x_intercepts interval
            midpoints <- sapply(x_intercepts, function(x) {
                sum(x) / 2
            })

            # Create a list of geom_text objects with the calculated midpoints
            text_geoms <- lapply(seq_along(labels), function(i) {
                geom_text(aes(x = midpoints[i], y = text_position, size = 7), label = labels[i], color = "grey80", angle = 90, vjust = 0.5, hjust = 0.5)
            })

            # Your additional code here if needed
        },
        error = function(e) {
            # Handle the error here
            cat("An error occurred:", conditionMessage(e), "\n")
            # You can add additional error-handling code if needed
        }
    )


    coeff_y_axis <- max(df_indi$score) / max(df_decade$score)
    myplot <- ggplot(df_decade, aes(x = decade, y = score)) +
        # geom_line(alpha = 0.3, linewidth = 0.5, colour = "darkblue") +
        # geom_bar(stat = "identity", color = "transparent", alpha = 0.2, fill = "blue") +
        geom_smooth(method = "loess", span = span, level = 0.95, linewidth = 1.5, colour = "darkblue") +

        # scale_x_continuous(breaks = seq(500, 1800, by = 500)) +
        scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        # ggtitle(name) +
        xlab("") +
        # scale_y_continuous(
        #     name = y_axis, sec.axis = sec_axis(trans = ~ . * coeff_y_axis, name = y_axis_2),
        #     limits = c(0, max(max(df_decade$score) + max(df_decade$score) * 0.1, na.rm = TRUE))
        # ) +

        scale_y_continuous(
            name = y_axis, sec.axis = sec_axis(trans = ~ . * coeff_y_axis, name = y_axis_2)
        ) +
        guides(color = guide_legend("region_name")) +
        scale_color_hue(direction = 1, h.start = 180) +
        geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
        geom_text_repel(data = head(df_indi[order(-df_indi$score), ], top_n_cps), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
        theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        theme(legend.position = "none") +
        theme_classic() +
        theme(axis.text.x = element_text(angle = 70, vjust = 0.5, size = 16)) + # Rotate x
        theme(plot.title = element_text(hjust = 0.5, size = 35)) +
        theme(legend.position = "none") +
        # theme(axis.text.x = element_text(size = 30)) +
        theme(axis.text.y = element_text(size = 30)) +
        theme(
            axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
        ) +
        vline_geoms +
        text_geoms
    return(myplot)
}


plot_unseen_index <- function(df_decade, df_indi, region_name, min_time, max_time, name, capita = FALSE, time_size = 15, x_intercepts, labels) {
    df_indi <- df_indi[which(df_indi$region_name == region_name), ]
    df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]

    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]

    df_decade$score <- log10(df_decade$score)
    df_decade$lower <- log10(df_decade$lower)
    df_decade$upper <- log10(df_decade$upper)

    upper_max <- max(df_decade$upper)
    upper_min <- min(df_decade$upper)

    original_range <- df_decade$upper - df_decade$lower
    original_mean_distance <- df_decade$upper - df_decade$score
    df_decade$upper <- (df_decade$upper - upper_min) / (upper_max - upper_min)

    # Adjust 'lower' and 'N_est' based on the normalized 'upper'
    df_decade$lower <- df_decade$upper - (original_range / (upper_max - upper_min))
    df_decade$score <- df_decade$upper - (original_mean_distance / (upper_max - upper_min))

    print(max(df_decade$upper))


    # df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))
    # df_decade$lower <- (df_decade$lower - min(df_decade$lower)) / (max(df_decade$lower) - min(df_decade$lower))
    # df_decade$upper <- (df_decade$upper - min(df_decade$upper)) / (max(df_decade$upper) - min(df_decade$upper))


    y_axis <- ifelse(capita,
        "Log Corrected Index per capita",
        "Log Corrected Index"
    )

    y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"

    color <- "#00bfc4"
    color <- "#f8766d"


    vline_geoms <- NULL
    text_geoms <- NULL

    tryCatch(
        {
            y_range <- range(df_decade$upper)
            # Parameters for region on the plot
            text_position <- 2 / 5 * diff(y_range)

            # Create a list of geom_vline objects
            vline_geoms <- lapply(x_intercepts, function(x) {
                geom_vline(xintercept = x, linetype = "dashed", color = "grey80")
            })

            # Calculate the midpoint of each x_intercepts interval
            midpoints <- sapply(x_intercepts, function(x) {
                sum(x) / 2
            })

            # Create a list of geom_text objects with the calculated midpoints
            text_geoms <- lapply(seq_along(labels), function(i) {
                geom_text(aes(x = midpoints[i], y = text_position, size = 7), label = labels[i], color = "grey80", angle = 90, vjust = 0.5, hjust = 0.5)
            })

            # Your additional code here if needed
        },
        error = function(e) {
            # Handle the error here
            cat("An error occurred:", conditionMessage(e), "\n")
            # You can add additional error-handling code if needed
        }
    )


    # min_value_left_axis <- min(df_decade$score, na.rm = TRUE)
    # min_value_right_axis <- min(df_indi$score, na.rm = TRUE)
    # coeff_y_axis <- max(df_indi$score) / max(df_decade$lower)

    myplot <- ggplot(df_decade, aes(x = decade, y = score, color = region_name)) +
        # geom_ribbon(data = df_decade, aes(x = decade, ymin = lower, ymax = upper), fill = "grey80", color = "lightblue") +

        geom_ribbon(data = df_decade, aes(x = decade, ymin = predict(loess(lower ~ decade, span = span)), ymax = predict(loess(upper ~ decade, span = span))), fill = "grey80", color = "lightblue") +
        geom_smooth(method = "loess", span = span, se = FALSE, , linewidth = 1.5, colour = "darkblue") +

        # geom_ribbon(data = df_decade, aes(x = decade, ymin = lower, ymax = upper), fill = "grey80", color = "lightblue") +
        # geom_line(aes(x = decade, y = score), size = 1, color = "darkblue") + # Add the line for "score"
        # geom_bar(stat = "identity", color = "transparent", alpha = 0.2, fill = "blue") +
        scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        xlab("") +
        # ggtitle(name) +
        # xlab("") +
        # scale_y_continuous(
        #     name = y_axis,
        #     limits = c(min_value_left_axis, NA), # Set the minimum for the left y-axis
        #     sec.axis = sec_axis(~ . * coeff_y_axis + (min_value_right_axis - min_value_left_axis * coeff_y_axis),
        #         name = y_axis_2
        #     )
        # ) + # Adjust the right y-axis +
        guides(color = guide_legend("region_name")) +
        scale_color_hue(direction = 1, h.start = 180) +
        # geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
        # geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 30), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
        theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        theme(legend.position = "none") +
        theme_classic() +
        theme(plot.title = element_text(hjust = 0.5, size = 35)) +
        theme(axis.text.x = element_text(angle = 70, vjust = 0.5, size = 16)) + # Rotate x

        theme(legend.position = "none") +
        # theme(axis.text.x = element_text(size = 30)) +
        theme(axis.text.y = element_text(size = 30)) +
        theme(
            axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
        ) +
        vline_geoms +
        text_geoms
    return(myplot)
}


plot_occupations <- function(df_decade, df_indi, region_name, min_time, max_time, graph_type = "global", name, time_size = 15, x_intercepts, labels) {
    df_indi <- df_indi[which(df_indi$region_name == region_name), ]
    df_indi <- df_indi[(df_indi$decade >= min_time) & (df_indi$decade <= max_time), ]

    # Group by occupation, region, and decade, and sum the scores
    df_decade <- df_decade %>%
        mutate(decade = floor(decade / 50) * 50) %>%
        group_by(occupations_name, region_name, decade) %>%
        summarise(score = sum(score))

    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]

    df_decade$score <- log10(df_decade$score)
    # df_decade$score <- (df_decade$score - min(df_decade$score)) / (max(df_decade$score) - min(df_decade$score))

    # Check the value of graph_type and assign labels accordingly
    if (graph_type == "capita") {
        y_axis <- "Log Cultural Index per capita"
    } else if (graph_type == "global") {
        y_axis <- "Log10 Count Occupations"
    } else if (graph_type == "complexity") {
        y_axis <- "Log Complexity Index"
    } else {
        # Handle unexpected or missing values of graph_type
        cat("Unknown graph_type:", graph_type)
    }


    y_axis_2 <- "Individual Immaterial Index (number of references in catalogs)"


    vline_geoms <- NULL
    text_geoms <- NULL

    tryCatch(
        {
            y_range <- range(df_decade$score)
            # Parameters for region on the plot
            text_position <- y_range[1] + 4 / 5 * diff(y_range)

            # Create a list of geom_vline objects
            vline_geoms <- lapply(x_intercepts, function(x) {
                geom_vline(xintercept = x, linetype = "dashed", color = "grey80")
            })

            # Calculate the midpoint of each x_intercepts interval
            midpoints <- sapply(x_intercepts, function(x) {
                sum(x) / 2
            })

            # Create a list of geom_text objects with the calculated midpoints
            text_geoms <- lapply(seq_along(labels), function(i) {
                geom_text(aes(x = midpoints[i], y = text_position, size = 7), label = labels[i], color = "grey80", angle = 90, vjust = 0.5, hjust = 0.5)
            })

            # Your additional code here if needed
        },
        error = function(e) {
            # Handle the error here
            cat("An error occurred:", conditionMessage(e), "\n")
            # You can add additional error-handling code if needed
        }
    )


    # Small multiple
    myplot <- ggplot(df_decade, aes(fill = occupations_name, y = score, x = decade)) +
        geom_bar(position = "stack", stat = "identity") +

        # geom_smooth(method = "loess", span = span, level = 0, linewidth = 1.5) +
        scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        xlab("") +
        scale_y_continuous(name = y_axis) +

        # scale_y_continuous(
        #     name = y_axis, sec.axis = sec_axis(trans = ~ . * coeff_y_axis, name = y_axis_2)
        # ) +
        scale_color_hue(direction = 1, h.start = 180) +
        # geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5) +
        # geom_text_repel(data = head(df_indi[order(-df_indi$score), ], top_n_cps), aes(x = decade, y = score / coeff_y_axis, label = individual_name, color = occupation_name), size = 3, alpha = 0.5, max.overlaps = 50) +
        # theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        theme_classic() +
        theme(axis.text.x = element_text(angle = 70, vjust = 0.5, size = 16)) +
        theme(plot.title = element_text(hjust = 0.5, size = 35)) +
        theme(axis.text.y = element_text(size = 30)) +
        theme(axis.title.y = element_text(size = 16))
    return(myplot)
}


plot_complexity <- function(df_decade, df_indi, region_name, min_time, max_time, name, capita = FALSE, time_size = 15, x_intercepts, labels) {
    # Filter by region
    df_decade <- df_decade[which(df_decade$region_name == region_name), ]
    df_decade <- df_decade[(df_decade$decade >= min_time) & (df_decade$decade <= max_time), ]

    # df_decade$mean_unique_occupations <- log10(df_decade$mean_unique_occupations)
    # df_decade$lower_bound <- log10(df_decade$lower_bound)
    # df_decade$upper_bound <- log10(df_decade$upper_bound)

    y_axis <- "Complexity Index"

    color <- "#00bfc4"
    color <- "#f8766d"


    myplot <- ggplot(df_decade, aes(x = decade, y = mean_unique_occupations, color = region_name)) +
        geom_ribbon(data = df_decade, aes(x = decade, ymin = predict(loess(lower_bound ~ decade, span = span)), ymax = predict(loess(upper_bound ~ decade, span = span))), fill = "grey80", color = "lightblue") +
        geom_smooth(method = "loess", span = span, se = FALSE, , linewidth = 1.5, colour = "darkblue") +
        scale_x_continuous(breaks = seq(floor(min_time / 100) * 100, floor(max_time / 100) * 100, 100)) +
        xlab("") +
        scale_y_continuous(
            name = y_axis
        ) +
        guides(color = guide_legend("region_name")) +
        scale_color_hue(direction = 1, h.start = 180) +
        # geom_point(data = df_indi, aes(x = decade, y = score / coeff_y_axis), alpha = 0.2, size = 0.5, colour = color) +
        # geom_text_repel(data = head(df_indi[order(-df_indi$score), ], 30), aes(x = decade, y = score / coeff_y_axis, label = individual_name), size = 3, alpha = 5, max.overlaps = 50, color = color) +
        theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "grey")) +
        theme(legend.position = "none") +
        theme_classic() +
        theme(plot.title = element_text(hjust = 0.5, size = 35)) +
        theme(axis.text.x = element_text(angle = 70, vjust = 0.5, size = 16)) + # Rotate x

        theme(legend.position = "none") +
        # theme(axis.text.x = element_text(size = 30)) +
        theme(axis.text.y = element_text(size = 30)) +
        theme(
            axis.title.y = element_text(size = 16) # Adjust the size for the y-axis label as needed
        )
    return(myplot)
}




# # Cultural Index Data
df_decade <- read.csv(file = "../results/df_region_score.csv", sep = ",", header = TRUE)
df_indi <- read.csv(file = "../results/df_individuals_score.csv", sep = ",", header = TRUE)
df_population <- read.csv("../../environnement_data/population_region_name.csv")
df_unseen <- read.csv(file = "../../unseen_species_model/results/estimations_charles_big_regions.csv", sep = ",", header = TRUE)
df_score_complexity <- read.csv(file = "../results/df_region_score_complexity.csv", sep = ",", header = TRUE)
df_score_occupation <- read.csv(file = "../results/df_region_score_occupations.csv", sep = ",", header = TRUE)

# Transformation
df_population <- df_population %>%
    rename(decade = year)

# Merge df_decade_poulation with df_population on the "region_name" column
df_decade_poulation <- inner_join(df_decade, df_population, by = c("region_name", "decade"))
df_decade_poulation <- df_decade_poulation %>%
    mutate(score = score / population)

df_unseen <- df_unseen %>%
    rename(score = N_est, region_name = region, lower = lower, upper = upper)

# Unseen Species Model per capita
# Merge df_decade_poulation with df_population on the "region_name" column
df_unseen_capita <- inner_join(df_unseen, df_population, by = c("region_name", "decade"))
df_unseen_capita$score <- df_unseen_capita$score / df_unseen_capita$population
df_unseen_capita$lower <- df_unseen_capita$lower / df_unseen_capita$population
df_unseen_capita$upper <- df_unseen_capita$upper / df_unseen_capita$population


span <- 0.2
top_n_cps <- 30

# Load the JSON file into an R object
parsed_data <- fromJSON("parameters_regions.json")

regions_names <- names(parsed_data)
# regions_names <- c("Chinese world")

# Loop through region names and display them
for (region_name in regions_names) {
    print(region_name)
    # Extract region_name for the current region

    region_parameters <- parsed_data[[region_name]]
    name <- region_parameters$`Region Parameters`$figure_name
    min_date_original <- region_parameters$`Region Parameters`$min_date
    max_date <- region_parameters$`Region Parameters`$max_date
    labels <- region_parameters$`Optional Region Information`$labels
    x_intercepts <- NULL

    # set the min date as the min date of the score region
    min_date <- min(df_decade$decade[df_decade$region_name == region_name])

    if (min_date < min_date_original) {
        min_date <- min_date_original
    }

    # Try get the periods names
    tryCatch(
        {
            x_intercepts_origin <- region_parameters$`Optional Region Information`$x_intercepts
            x_intercepts <- split(x_intercepts_origin, seq_len(nrow(x_intercepts_origin)))
        },
        error = function(e) {
            # Handle the error here
            cat("No information on periods for", region_name, "\n")
            # You can add additional error-handling code if needed
        }
    )


    #   Occupation
    tryCatch(
        {
            plot_trend_occupation <- plot_occupations(df_score_occupation, df_indi, region_name, min_date, max_date, graph_type = "global", name, 8, x_intercepts, labels)
            ggsave(file.path("results_occupations", paste0(region_name, ".png")), plot = plot_trend_occupation, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save cultural index for: ", region_name, "\n")
        }
    )


    # Cultural Index
    tryCatch(
        {
            plot_trend <- plot_cultural_index(df_decade, df_indi, region_name, min_date, max_date, graph_type = "global", name, 8, x_intercepts, labels)
            ggsave(file.path("results", paste0(region_name, ".png")), plot = plot_trend, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save cultural index for: ", region_name, "\n")
        }
    )

    # Cultural Index per capita

    tryCatch(
        {
            plot_trend_population <- plot_cultural_index(df_decade_poulation, df_indi, region_name, min_date, max_date, graph_type = "capita", name, time_size = 8, x_intercepts = x_intercepts, labels = labels)
            ggsave(paste0("results_capita/", region_name, ".png"), plot = plot_trend_population, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save cultural index per capita for: ", region_name)
        }
    )


    # Unseen Species Model
    tryCatch(
        {
            plot_trend_unseen <- plot_unseen_index(df_unseen, df_indi, region_name, min_date, max_date, name = name, capita = FALSE, time_size = 8, x_intercepts = x_intercepts, labels = labels)
            ggsave(paste0("results_unseen/", region_name, ".png"), plot = plot_trend_unseen, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save Unseen index for: ", region_name)
        }
    )
    # Unsee per capita
    tryCatch(
        {
            plot_trend_unseen <- plot_unseen_index(df_unseen_capita, df_indi, region_name, min_date, max_date, name = name, capita = TRUE, time_size = 8, x_intercepts = x_intercepts, labels = labels)
            ggsave(paste0("results_unseen_capita/", region_name, ".png"), plot = plot_trend_unseen, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save Unseen index per capita for: ", region_name)
        }
    )

    # Complexity
    tryCatch(
        {
            plot_trend <- plot_complexity(df_score_complexity, df_indi, region_name, min_date, max_date, name, 8, x_intercepts, labels)
            ggsave(file.path("results_complexity", paste0(region_name, ".png")), plot = plot_trend, dpi = 300, width = 10, height = 8)
        },
        error = function(e) {
            # Handle the error here
            cat("cant's save complexity index for: ", region_name, "\n")
        }
    )
}
warnings()
