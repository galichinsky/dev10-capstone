# Quality of Life vs Happiness: Technical Report

## Questions Asked
1. What are the key factors that correlate with a high quality of life?
2. How does happiness correlate with quality of life metrics?
3. Which regions of the world have the highest and lowest quality of life and happiness scores?
4. What is the relationship between GDP and quality of life metrics?
5. How do environmental factors (e.g., climate) impact happiness and quality of life?
6. What role does social support play in determining happiness and quality of life?
7. Which countries are outliers in terms of happiness or quality of life?
8. How strong of a relationship do quality of life and happiness have?

---

## Datasets Used
- **Quality of Life Data**: Metrics such as stability, rights, health, safety, and climate.
- **Happiness Data**: Ladder scores, GDP, social support, life expectancy, freedom, and corruption perceptions.
- **Source**: Data was aggregated from publicly available datasets (e.g., World Happiness Report, World Bank).

---

## Datasets Used
- **Quality of Life Data**: 
    - Retrieved `quality_of_life.csv` dataset from kaggle. The data was collected from: [worlddata.info](https://www.worlddata.info/quality-of-life.php#google_vignette)
- **Happiness Data**:
    - `world-happiness-report-2022.xls` dataset was retrieved from [worldhappiness.report](https://worldhappiness.report/)

---

## ETL Process
1. **Extract**:
    - Downloaded the datasets from the respective sources.
    - Loaded the datasets into Pandas DataFrames.
2. **Transform**:
    - Cleaned the data by removing unnecessary columns and renaming them for consistency.
    - Removed rows with missing values.
    - Converted data types where necessary (e.g., converting strings to numeric).
    - Merged the datasets on the country name to create a comprehensive dataset.
3. **Load**:
    - Data was loaded into a MySQL database for further analysis.

---

## Technologies Used
- **Python**:
    - Libraries: `pandas`, `numpy`, `plotly`, `dash`, `statsmodels`, `dynaconf`, `sqlalchemy`.
- **SQL**:
    - Used for querying and extracting data from relational databases.
- **Docker**:
    - Containerized the application for easy deployment and scalability.
- **Airflow**:
    - Used for scheduling and automating the ETL process.
- **Jupyter Notebook**:
    - Used for exploratory data analysis and visualization.
- **MySQL**:
    - Used for storing and managing the datasets.
- **Plotly**:
    - Used for creating scatter plots, bar graphs, and trendline visualizations.

---

## Machine Learning
- **OLS Regression**:
  - Used to predict happiness and quality of life scores based on key metrics.
  - R² values:
    - Happiness Model: `0.88`
    - Quality of Life Model: `0.96`
  - These models helped identify outliers and quantify the strength of relationships between variables.

---

## Conclusions
1. What are the key factors that correlate with a high quality of life?

    #### Strong, Positive Relationships with QOL
    - stability: `0.83`
    - rights: `0.89`
    - health: `0.91`
    - safety: `0.76`
    - log_gdp: `0.89`
    - social support: `0.70`
    - healthy_life_expectancy: `0.88`
    - happiness: `0.76`

2. How does happiness (ladder score) correlate with quality of life metrics?

    - Countries with higher happiness scores tend to have better quality of life indicators, such as strong healthcare systems, economic prosperity, and personal freedoms.
    - Health and economic factors (e.g., GDP, life expectancy) are the most influential metrics for happiness.
    - Safety and social support also play important roles but are slightly less correlated compared to health and economic factors.

3. Which regions of the world have the highest and lowest quality of life and happiness scores?
    - Compare regional trends to identify disparities in well-being.

        - High/Low QOL: Oceania/Africa
        - High/Low Happiness: Europe/Africa

4. What is the relationship between GDP (log_gdp) and quality of life metrics?
    - Determine if higher economic output translates to better quality of life.

         - Based on an R² value of 0.802, there is a strong positive relationship between GDP (log_gdp) and quality of life metrics. This indicates that approximately 80.2% of the variance in quality of life metrics can be explained by GDP. Higher economic output is strongly associated with better quality of life indicators.

5. How do environmental factors (e.g., climate) impact happiness and quality of life?
    - Explore whether countries with better environmental conditions report higher well-being.

        - With an R² value of 0.12 for climate vs quality of life, the relationship is weak, suggesting that climate has a minimal impact on quality of life metrics.
        - Similarly, an R² value of 0.24 for climate vs happiness indicates a modest relationship, implying that while climate may influence happiness to some extent, it is not a dominant factor.
        - Other factors, such as economics, health, and social metrics, likely play a more significant role in determining both quality of life and happiness.

6. What role does social support play in determining happiness and quality of life?
    - Examine the influence of social support on well-being metrics.
        1. Social Support vs Happiness (R² = 0.74)
            - Social support has a strong positive influence on happiness. An R² value of 0.74 indicates that 74% of the variance in happiness can be explained by social support.
            - Countries with higher social support tend to have significantly higher happiness scores.
        2. Social Support vs Quality of Life (R² = 0.50)
            - Social support has a moderate positive influence on quality of life. An R² value of 0.50 indicates that 50% of the variance in quality of life can be explained by social support.
            - While social support contributes to quality of life, other factors like economic stability (GDP), healthcare, and safety likely play a larger role.
        - While social support is a key driver of emotional well-being, improving quality of life requires addressing a broader range of factors.

7. Which countries are outliers in terms of happiness or quality of life?
- Identify countries that perform significantly better or worse than expected based on their metrics.
    - The OLS model for happiness has an R² value of 0.88, indicating that 88% of the variance in happiness scores is explained by the predictors.
    - The OLS model for quality of life has an R² value of 0.96, indicating that 96% of the variance in quality of life scores is explained by the predictors.
    - These models help identify countries that perform significantly better or worse than expected based on their metrics.

    - Australia's actual QOL score is much higher than predicted by the OLS model, which means there are factors contributing to its high QOL that are not fully captured by the predictors in the model.
    - Both Sri Lanka and Lebanon have actual happiness scores that are lower than predicted by the OLS model, indicating that there are factors contributing to their lower happiness that are not fully captured by the predictors in the model.

8. How strong of a relationship do quality of life and happiness have?
    - Strong Positive Relationship: A correlation of 0.77 indicates that countries with higher quality of life tend to have higher happiness scores.
    - R² Value: The R² value of 0.59 shows that quality of life explains a significant portion of the variance in happiness, but other factors also play a role.



