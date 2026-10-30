#!/usr/bin/env Rscript
# Public-data R demonstration: DOJ county counts + audited DOF population totals.
#
# Run from the repository root:
#   Rscript R/pooled_count_ratio_demo.R
#
# This is NOT the original IPUMS demographic-rate analysis. It independently
# recomputes pooled county ratios from the two published aggregate tables.
# It cannot reconstruct the underlying yearly DOF populations from pooled totals.

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(ggplot2)
})

STUDY_YEARS <- 2018:2022
EXPECTED_COUNT <- 10187

fail <- function(message) stop(message, call. = FALSE)

check_columns <- function(data, required, label) {
  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    fail(paste(label, "missing columns:", paste(missing, collapse = ", ")))
  }
}

calculate_pooled_count_ratios <- function(published, denominators,
                                          full_audit = TRUE) {
  check_columns(published,
                c("county", "year", "published_homicide_crimes"),
                "DOJ county-year table")
  check_columns(denominators,
                c("county", "published_homicide_count",
                  "population_person_years", "years_observed",
                  "mean_annual_population", "annualized_count_per_100k"),
                "DOF-derived pooled table")

  if (anyNA(published) || anyNA(denominators)) {
    fail("Missing source values: inspect inputs before computing ratios.")
  }
  if (anyDuplicated(published[c("county", "year")]) ||
      anyDuplicated(denominators["county"])) {
    fail("Non-unique county-year or county keys would multiply join rows.")
  }
  if (!all(published$year %in% STUDY_YEARS) ||
      any(published$county == "") || any(denominators$county == "")) {
    fail("Invalid years or blank county names.")
  }
  if (!is.numeric(published$published_homicide_crimes) ||
      any(!is.finite(published$published_homicide_crimes)) ||
      any(published$published_homicide_crimes < 0) ||
      any(published$published_homicide_crimes !=
          floor(published$published_homicide_crimes))) {
    fail("DOJ published counts must be finite, nonnegative whole numbers.")
  }
  if (!is.numeric(denominators$population_person_years) ||
      any(!is.finite(denominators$population_person_years)) ||
      any(denominators$population_person_years <= 0)) {
    fail("DOF population-person-years must be finite and positive.")
  }
  if (!setequal(published$county, denominators$county)) {
    fail("The 58-county sets do not match between the two inputs.")
  }
  if (any(denominators$years_observed != length(STUDY_YEARS))) {
    fail("All counties must have five annual population observations.")
  }
  if (any(abs(denominators$mean_annual_population -
              round(denominators$population_person_years / 5)) > 0)) {
    fail("Average population does not reconcile to population-person-years.")
  }

  if (full_audit) {
    annual <- published %>%
      count(year, name = "n_counties")
    if (nrow(published) != 290 ||
        nrow(denominators) != 58 ||
        !setequal(annual$year, STUDY_YEARS) ||
        any(annual$n_counties != 58) ||
        sum(published$published_homicide_crimes) != EXPECTED_COUNT) {
      fail("Inputs do not match audited 58-county, 2018-2022 DOJ totals.")
    }
  }

  county_counts <- published %>%
    group_by(county) %>%
    summarise(published_homicide_count = sum(published_homicide_crimes),
              observed_years = n_distinct(year),
              .groups = "drop")

  reference <- denominators %>%
    select(county,
           expected_count = published_homicide_count,
           population_person_years, years_observed,
           mean_annual_population,
           expected_ratio = annualized_count_per_100k)

  result <- county_counts %>%
    left_join(reference, by = "county") %>%
    mutate(annualized_count_per_100k =
             round(published_homicide_count / population_person_years *
                     100000, 2))

  if (nrow(result) != nrow(reference) ||
      anyNA(result) ||
      any(result$observed_years != result$years_observed) ||
      any(result$published_homicide_count != result$expected_count) ||
      any(abs(result$annualized_count_per_100k - result$expected_ratio) >
            0.000001)) {
    fail("Join, reported counts, or independently calculated ratios disagree.")
  }

  result %>%
    select(county, published_homicide_count, population_person_years,
           years_observed, mean_annual_population,
           annualized_count_per_100k) %>%
    arrange(desc(mean_annual_population))
}

plot_pooled_comparison <- function(ratios) {
  # Preselect the 12 largest counties by population, NOT by outcome.
  top <- ratios %>%
    slice_max(mean_annual_population, n = 12, with_ties = FALSE) %>%
    arrange(mean_annual_population)

  graph <- bind_rows(
    top %>% transmute(county, measure = "Five-year published count",
                      value = published_homicide_count),
    top %>% transmute(county,
                      measure = "Annualized count per 100,000 residents",
                      value = annualized_count_per_100k)
  )
  graph$county <- factor(graph$county, levels = top$county)

  ggplot(graph, aes(x = value, y = county)) +
    geom_col(fill = "#2374AB", width = 0.7) +
    facet_wrap(~ measure, scales = "free_x", ncol = 2) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.08))) +
    labs(
      title = "Published homicide counts versus population-adjusted ratios",
      subtitle = "California's 12 most populous counties | 2018-2022 pooled",
      x = NULL, y = NULL,
      caption = paste(
        "Sources: California DOJ, Homicide in California 2022, Table 14;",
        "CA DOF E-2 July 1 population estimates (mixed vintages).\n",
        "Reporting-agency county is not victim residence.",
        "Ratios are descriptive, not individual risk estimates."
      )
    ) +
    theme_minimal(base_size = 11) +
    theme(panel.grid.major.y = element_blank(),
          strip.text = element_text(face = "bold"),
          plot.caption = element_text(hjust = 0, size = 8),
          plot.title = element_text(face = "bold"))
}

main <- function() {
  counts_path <- "reports/doj_published_table14_county_year.csv"
  denom_path <- "reports/published_county_pooled_2018_2022.csv"
  if (!file.exists(counts_path) || !file.exists(denom_path)) {
    fail("Run from the repository root (both reports/*.csv files required).")
  }

  published <- read_csv(
    counts_path, show_col_types = FALSE,
    col_types = cols(county = col_character(), year = col_integer(),
                     published_homicide_crimes = col_double())
  )
  denominators <- read_csv(
    denom_path, show_col_types = FALSE,
    col_types = cols(
      county = col_character(),
      published_homicide_count = col_double(),
      population_person_years = col_double(),
      years_observed = col_integer(),
      mean_annual_population = col_double(),
      annualized_count_per_100k = col_double()
    )
  )
  stop_for_problems(published)
  stop_for_problems(denominators)

  ratios <- calculate_pooled_count_ratios(published, denominators)
  dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
  dir.create("figures", showWarnings = FALSE, recursive = TRUE)
  write_csv(ratios, "data/processed/r_published_county_pooled_2018_2022.csv")

  figure <- plot_pooled_comparison(ratios)
  ggsave("figures/r_published_count_vs_population_adjusted.png",
         plot = figure, width = 12, height = 7, dpi = 180)

  cat("Validated", nrow(ratios), "counties across five years.\n")
  cat("Published DOJ count:", sum(ratios$published_homicide_count), "\n")
  cat("Recomputed rates match published aggregate reference.\n")
  cat("Saved: data/processed/r_published_county_pooled_2018_2022.csv\n")
  cat("Saved: figures/r_published_count_vs_population_adjusted.png\n")
}

if (sys.nframe() == 0L) main()
