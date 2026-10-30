# Reproducible tests with invented data; no private or downloaded inputs.
# Run from repository root: Rscript R/tests/test_pooled_count_ratio_demo.R

source("R/pooled_count_ratio_demo.R")

published <- data.frame(
  county = rep(c("Alpha County", "Beta County"), each = 5),
  year = rep(2018:2022, times = 2),
  published_homicide_crimes = c(1, 2, 3, 4, 5, 0, 0, 2, 2, 1)
)

denominators <- data.frame(
  county = c("Alpha County", "Beta County"),
  published_homicide_count = c(15, 5),
  population_person_years = c(500000, 250000),
  years_observed = c(5L, 5L),
  mean_annual_population = c(100000, 50000),
  annualized_count_per_100k = c(3, 2)
)

result <- calculate_pooled_count_ratios(
  published, denominators, full_audit = FALSE
)
stopifnot(nrow(result) == 2L)
stopifnot(result$county[1] == "Alpha County")
stopifnot(identical(result$annualized_count_per_100k, c(3, 2)))
stopifnot(sum(result$published_homicide_count) == 20)

expect_failure <- function(expr) {
  outcome <- tryCatch(force(expr), error = function(err) err)
  if (!inherits(outcome, "error")) {
    stop("Expected a validation failure but calculation succeeded.")
  }
}

duplicates <- rbind(published, published[1, ])
expect_failure(calculate_pooled_count_ratios(
  duplicates, denominators, full_audit = FALSE
))

bad_denominators <- denominators
bad_denominators$published_homicide_count[1] <- 16
expect_failure(calculate_pooled_count_ratios(
  published, bad_denominators, full_audit = FALSE
))

zero_population <- denominators
zero_population$population_person_years[2] <- 0
expect_failure(calculate_pooled_count_ratios(
  published, zero_population, full_audit = FALSE
))

cat("R synthetic tests passed: pooled ratios and validation safeguards.\n")
