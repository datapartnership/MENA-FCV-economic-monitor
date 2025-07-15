# Measuring Global Migration Flows using Online data

## Data Description

A study by {cite:t}`chi_measuring_2025` estimate countries migration flow for 181 countries at monthly basis from January 2019 to December 2022 using an alternative data, Facebook's privacy-protected records of their three billion users. This represents approximately 79.2% of the global population (97.4% when including experimental estimates for China). Their estimates can be produced at speed faster than traditional methods and cover a wider range of countries, including those with limited migration data.

Their definition of migration is based on the United Nations' recommended definition, which states that migration occurs when an individual has resided in a country for more than one year and then moves to another country where they reside for more than one year. This excludes temporary movements and transit migration lasting less than 12 months.

## Methodology

The methodology used in the study consists of the following steps:

- Data Collection: The researchers collected Facebook's privacy-protected records of their three billion users, which included self-reported locations and IP addresses used to connect to Facebook.

- Migration Detection: They estimated a predicted country location for each user based on a combination of signals, including self-reported locations and IP addresses. A segment-based method was used to create a time frame for each user's country location.

- Migration Definition: Migration was defined as living in one country for the majority of a 12-month period before moving to another country for the majority of the following 12 months, aligning with the United Nations' definition of migration.

- Data Aggregation: The data was aggregated to monthly migration flows between countries, focusing on the number of migrants moving from one country to another.

- Data Weighting: Since Facebook's data is not representative of the global population, a weighting scheme was applied to adjust for selection bias. This scheme accounts for the fact that wealthier individuals are more likely to use Facebook and migrate, especially in poorer countries. The researchers refer to this as the "selection rate," which adjusts migration flows based on Facebook usage and income levels at the country level.

- Data Privacy: To preserve the privacy of individual-level data, they utilized differential privacy techniques by adding noise to the estimates. This ensures that individual users' data cannot be re-identified while still providing useful aggregate statistics.

## Validation

The researchers validated the migration estimates by comparing them against official statistics from various countries and international organizations. They primarily compared their estimate to New Zealand's official migration statistics. and the European Union's Eurostat data, as these datasets are considered to be of high quality.

Compared to the New Zealand's official migration statistics, the researchers found that their estimates were closely aligned with a correlation of 0.98 and managed to capture the temporal patterns of migration flows. This suggests that their methodology is robust and produces reliable migration flow estimates. A similar validation was conducted with the European Union's Eurostat data, which also showed a high correlation of 0.94 between their estimates and official statistics.

## Limitation

While the methodology used in the study is innovative and provides valuable insights into global migration flows, it has several limitations. First, the differential privacy process, which adds noise to the estimates to protect individual privacy and censor negative values at zero, can lead to systematic biases in the estimates, particularly for small migration flows. 

Second, a policy-specific migration gap can occur when unique migration policies do not follow typical selection patterns, leading to estimation errors. For example, the Samoa-New Zealand migration flow is influenced by the Samoan Quota system, which allows 0.5% of Samoa's population to migrate annually via a lottery system, creating flows that do not match the model's assumptions about migrant selection.

Lastly, discrepancies can arise when comparing Facebook's estimates to official statistics that use different migration definitions. For instance, some countries, like Slovakia, report only permanent residents rather than all individuals meeting the UN's 12-month residency definition, making validation comparisons problematic.

```{bibliography}
```