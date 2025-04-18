import logging
import os
import pandas as pd
from sqlalchemy import create_engine
from dynaconf import Dynaconf

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)

class ETLProcessor:
    def __init__(self, qol_path: str, whr_path: str, engine):
        self.qol_path = qol_path
        self.whr_path = whr_path
        self.engine = engine
        
    def extract(self):
        log.info("Extracting data...")
        df_qol = pd.read_csv(self.qol_path)
        log.info(f"Extracted Quality of Life data: {df_qol.shape[0]} rows")
        
        df_whr = pd.read_excel(self.whr_path)
        log.info(f"Extracted World Happiness Report data: {df_whr.shape[0]} rows")
        return df_qol, df_whr
    
    def transform(self, df_qol, df_whr):
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
        df_whr.drop(columns=['RANK', 'Whisker-high', 'Whisker-low'], inplace=True)
        df_whr.columns = ['country_name', 'happiness', 'dystopia', 'log_gdp', 'social_support', 'healthy_life_expectancy', 'freedom', 'generosity', 'perceptions_of_corruption']
        df_whr['country_name'] = df_whr['country_name'].str.replace('*', '', regex=False)    
        
        return df_qol, df_whr
    
    def load(self, df_qol, df_whr):
        log.info("Loading data into the database...")

        # Combine country names from both datasets
        countries_qol = df_qol['country_name'].unique()
        countries_whr = df_whr['country_name'].unique()
        all_countries = pd.DataFrame(
            {'country_name': pd.unique(pd.concat([pd.Series(countries_qol), pd.Series(countries_whr)]))}
        )

        # Load countries into the 'country' table
        all_countries.to_sql('country', con=self.engine, if_exists='append', index=False)
        log.info(f"Loaded {len(all_countries)} countries into the 'country' table.")

        # Verify the data was loaded
        loaded_countries = pd.read_sql("SELECT * FROM country", con=self.engine)
        log.info(f"Countries in the database:\n{loaded_countries}")
        print(loaded_countries)
        
    def process(self):
        log.info("Starting ETL process...")
        df_qol, df_whr = self.extract()
        df_qol, df_whr = self.transform(df_qol, df_whr)
        self.load(df_qol, df_whr)
        log.info("ETL process completed successfully.")
        
if __name__ == "__main__":
    
    # Paths to the data files
    qol_path = os.path.join(os.path.dirname(__file__), "quality_of_life.csv")
    whr_path = os.path.join(os.path.dirname(__file__), "world-happiness-2022.xls")
    
    def build_engine():
        settings = Dynaconf(envvar_prefix="DB", load_dotenv=True)
        return create_engine(settings.ENGINE_URL, echo=True)
    
    engine = build_engine()
    
    with engine.connect() as con, con.begin():
        processor = ETLProcessor(
            qol_path,
            whr_path,
            engine
        )
        processor.process()
        
    engine.dispose()