library(nlme)

# path_to_stats = 'data_stats'

data <- read.table("data_stats/data_stats_90_percent.csv",
    header = TRUE,
    sep = ","
)


# data$CCPpc = data$cultural_score_interpolared / data$population_interpolated
# dataSci$CCPpc = dataSci$cultural_score_interpolared / dataSci$population_interpolated


model_1 <- lme(gdp_per_capita ~ cultural_score_interpolated + year,
    random = ~ 1 | region_code,
    data = data
)

# summary(model_1)

model_cor_1 <- update(model_1, correlation = corAR1(form = ~ year | region_code))

summary(model_cor_1)
