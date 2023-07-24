library(nlme)

# path_to_stats = 'data_stats'

data <- read.table("data_stats_35.csv",
    header = TRUE,
    sep = ","
)

# data$CCPpc = data$cultural_score_interpolared / data$population_interpolated
# dataSci$CCPpc = dataSci$cultural_score_interpolared / dataSci$population_interpolated


model_1 <- lme(gdp_per_capita ~ score_cap + year,
    random = ~ 1 | region_name,
    data = data
)


# 0.79
# N_est_cap
# score_cap
# score

# summary(model_1)

model_cor_1 <- update(model_1, correlation = corAR1(form = ~ year | region_name))

summary(model_cor_1)

residuals <- resid(model_cor_1)

# Calculate the total sum of squares
total_sum_of_squares <- sum((data$gdp_per_capita - mean(data$gdp_per_capita))^2)

# Calculate the residual sum of squares
residual_sum_of_squares <- sum(residuals^2)

# Calculate the R-squared value
r_squared <- 1 - (residual_sum_of_squares / total_sum_of_squares)

# Print the R-squared value
print(paste("R-squared:", r_squared))
