import pandas as pd
import numpy as np

def function_transformer(dataframe, dataframe_type_chart):
   # Funzione per calcolare i moltiplicatori di tipo
   def get_dual_multiplier(df, atk_col, def1_col, def2_col, newcol):
      tmp = dataframe_type_chart.rename(columns={
         'attack': atk_col,
         'defense1': def1_col,
         'defense2': def2_col
      })
      df = df.merge(
         tmp[[atk_col, def1_col, def2_col, 'multiplier']],
         on=[atk_col, def1_col, def2_col],
         how='left'
      ).rename(columns={'multiplier': newcol})
      df[newcol] = df[newcol].fillna(1.0)
      return df
   # Aggiunta dei moltiplicatori di tipo
   dataframe: pd.DataFrame = dataframe.copy()
   dataframe: pd.DataFrame = get_dual_multiplier(dataframe, 'Type 1_F', 'Type 1_S', 'Type 2_S', 'F1_to_S')
   dataframe: pd.DataFrame = get_dual_multiplier(dataframe, 'Type 2_F', 'Type 1_S', 'Type 2_S', 'F2_to_S')
   dataframe: pd.DataFrame = get_dual_multiplier(dataframe, 'Type 1_S', 'Type 1_F', 'Type 2_F', 'S1_to_F')
   dataframe: pd.DataFrame = get_dual_multiplier(dataframe, 'Type 2_S', 'Type 1_F', 'Type 2_F', 'S2_to_F')
   # Calcolo dell'efficacia di tipo
   dataframe['Type Effectiveness_F'] = dataframe['F1_to_S'] * dataframe['F2_to_S']
   dataframe['Type Effectiveness_S'] = dataframe['S1_to_F'] * dataframe['S2_to_F']
   dataframe.drop(columns=['F1_to_S', 'F2_to_S', 'S1_to_F', 'S2_to_F'], inplace=True)
   # Rimozione delle colonne di tipo originali
   dataframe.drop(columns=['Type 1_F', 'Type 2_F', 'Type 1_S', 'Type 2_S'], inplace=True)
   # Rimpiazzo delle statistiche con la differenza delle statistiche tra i due pokemon
   stats: list[str] = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
   for stat in stats:
      dataframe[f"delta_{stat}"] = dataframe[f'{stat}_F'] - dataframe[f'{stat}_S']
      dataframe.drop(columns=[f'{stat}_F', f'{stat}_S'], inplace=True)
   # Rimozione delle colonne non necessarie
   return dataframe.drop(columns=['Name_F', 'Name_S', 'Generation_F', 'Generation_S'])