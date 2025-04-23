import logging
import os
import pandas as pd
from sqlalchemy import create_engine
from dynaconf import Dynaconf

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

class ETLProcessor:
    def __init__(self, qol_path: str, whr_path: str, regions_path: str, engine):
        self.qol_path = qol_path
        self.whr_path = whr_path
        self.regions_path = regions_path
        self.engine = engine
        
    def extract(self):
        log.info("Extracting data...")
        df_qol = pd.read_csv(self.qol_path)
        log.info(f"Extracted Quality of Life data: {df_qol.shape[0]} rows")
        
        df_whr = pd.read_excel(self.whr_path)
        log.info(f"Extracted World Happiness Report data: {df_whr.shape[0]} rows")
        
        df_regions = pd.read_csv(self.regions_path)
        log.info(f"Extracted country regions data: {df_regions.shape[0]} rows")
        
        return df_qol, df_whr, df_regions
    
    def transform(self, df_qol, df_whr, df_regions):
        log.info("Transforming data...")
        
        # transform Quality of Life data
        # Define the weights for each factor
        df_qol.rename(columns={'country': 'country_name'}, inplace=True)
        
        weights = {
            'stability': 0.15,
            'rights': 0.20,
            'health': 0.25,
            'safety': 0.10,
            'climate': 0.15,
            'costs': 0.15,
            'popularity': 0.10
        }

        df_qol['qol_index'] = (
            df_qol['stability'] * weights['stability'] +
            df_qol['rights'] * weights['rights'] +
            df_qol['health'] * weights['health'] +
            df_qol['safety'] * weights['safety'] +
            df_qol['climate'] * weights['climate'] +
            df_qol['costs'] * weights['costs'] +
            df_qol['popularity'] * weights['popularity']
        )
        log.info("Transformed Quality of Life data adding qol_index")
            
        # transform World Happiness Report data
        df_whr.dropna(inplace=True)
        df_whr.drop(
        columns=[
            'Standard error of ladder score', 'upperwhisker', 'lowerwhisker',
            'Explained by: Log GDP per capita', 'Explained by: Social support',
            'Explained by: Healthy life expectancy', 'Explained by: Freedom to make life choices',
            'Explained by: Generosity', 'Explained by: Perceptions of corruption',
            'Ladder score in Dystopia', 'Dystopia + residual'
        ],
        inplace=True
        )

        df_whr.columns = [
        'country_name', 'happiness', 'log_gdp', 'social_support',
        'healthy_life_expectancy', 'freedom', 'generosity', 'perceptions_of_corruption'
        ]    
        
        df_regions['country_name'] = df_regions['country_name'].astype(str)
        
        return df_qol, df_whr, df_regions
    
    def load(self, df_qol, df_whr, df_regions):
        log.info("Loading data into the database...")

        # Combine country names from both datasets
        countries_qol = df_qol['country_name'].unique()
        countries_whr = df_whr['country_name'].unique()
        all_countries = pd.DataFrame(
            {'country_name': pd.unique(pd.concat([pd.Series(countries_qol), pd.Series(countries_whr)]))}
        )
        
        # Merge region data with combined counrty list
        all_countries = pd.merge(all_countries, df_regions, on='country_name', how='left')
        
        # # Check for missing regions
        # missing_regions = all_countries[all_countries['region'].isnull()]
        # if not missing_regions.empty:
        #     log.error(f"Missing regions for the following countries: {missing_regions['country_name'].tolist()}")
        #     raise ValueError("Some countries are missing region data. Please update the 'country_regions.csv' file.")


        # Load countries into the 'country' table
        all_countries.to_sql('country', con=self.engine, if_exists='append', index=False)
        log.info(f"Loaded {len(all_countries)} countries into the 'country' table.")
        
        # grab the country ids
        country_df = pd.read_sql("SELECT * FROM country", con=self.engine)
        
        df_qol['country_name'] = df_qol['country_name'].astype(str)
        df_whr['country_name'] = df_whr['country_name'].astype(str)
        country_df['country_name'] = country_df['country_name'].astype(str)
        
        df_qol = pd.merge(df_qol, country_df, on='country_name', how='left')
        df_whr = pd.merge(df_whr, country_df, on='country_name', how='left')
        
        if df_qol['country_id'].isnull().any():
            log.error("Some country names in Quality of Life data do not match the database.")
        
        # load quality of life data to quality table
        quality_columns = ['qol_index', 'stability', 'rights', 'health', 'safety', 'climate', 'costs', 'popularity', 'country_id']
        df_qol[quality_columns].to_sql('quality', con=self.engine, if_exists='append', index=False)
        log.info(f"Loaded {len(df_qol)} rows into the 'quality' table.")
        
        # load world happiness report data to happiness table
        happiness_columns = ['happiness', 'log_gdp', 'social_support', 'healthy_life_expectancy', 'freedom', 'generosity', 'perceptions_of_corruption', 'country_id']
        df_whr[happiness_columns].to_sql('happiness', con=self.engine, if_exists='append', index=False)
        log.info(f"Loaded {len(df_whr)} rows into the 'happiness' table.")
        
    def process(self):
        log.info("Starting ETL process...")
        df_qol, df_whr, df_regions = self.extract()
        df_qol, df_whr, df_regions = self.transform(df_qol, df_whr, df_regions)
        self.load(df_qol, df_whr, df_regions)
        log.info("ETL process completed successfully.")
        
if __name__ == "__main__":
    
    # Paths to the data files
    qol_path = os.path.join(os.path.dirname(__file__), "quality_of_life.csv")
    whr_path = os.path.join(os.path.dirname(__file__), "world-happiness-2022.xls")
    regions_path = os.path.join(os.path.dirname(__file__), "country_regions.csv")
    
    def build_engine():
        settings = Dynaconf(envvar_prefix="DB", load_dotenv=True)
        return create_engine(settings.ENGINE_URL, echo=True)
    
    engine = build_engine()
    
    with engine.connect() as con, con.begin():
        processor = ETLProcessor(
            qol_path,
            whr_path,
            regions_path,
            engine
        )
        processor.process()
        
    engine.dispose()