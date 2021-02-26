import argparse
import lightgbm as lgbm
import catboost as ctb
from utils import load_json
from data import SF1Data
from features import QuarterlyFeatures, BaseCompanyFeatures, FeatureMerger, \
                     QuarterlyDiffFeatures
from targets import QuarterlyDiffTarget
from models import GroupedOOFModel, AnsambleModel
from metrics import median_absolute_relative_error
from pipelines import BasePipeline


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('--config_path', type=str)
    args = parser.parse_args()
    
    config = load_json(args.config_path)
    pipeline_config = config['pipelines']['marketcap']

    data_loader = SF1Data(config['sf1_data_path'])
    tickers_df = data_loader.load_tickers(
        currency=pipeline_config['currency'],
        scalemarketcap=pipeline_config['scalemarketcap'])
    ticker_list = tickers_df['ticker'].unique().tolist()

    fc1 = QuarterlyFeatures(
        columns=pipeline_config['quarter_columns'],
        quarter_counts=pipeline_config['quarter_counts'],
        max_back_quarter=pipeline_config['max_back_quarter'])

    fc2 = BaseCompanyFeatures(
        cat_columns=pipeline_config['cat_columns'])
        
    fc3 = QuarterlyDiffFeatures(
        columns=pipeline_config['quarter_columns'],
        compare_idxs=[1, 4],
        max_back_quarter=pipeline_config['max_back_quarter'])
                            
    feature = FeatureMerger(fc1, fc2, on='ticker')
    feature = FeatureMerger(feature, fc3, on=['ticker', 'date'])

    target = QuarterlyDiffTarget(col='marketcap')

    base_models = [lgbm.sklearn.LGBMRegressor(),
                   ctb.CatBoostRegressor(verbose=False)]
                   
    ansamble = AnsambleModel(base_models=base_models, 
                             bagging_fraction=0.7, model_cnt=20)

    model = GroupedOOFModel(ansamble, group_column='ticker', fold_cnt=5)

    pipeline = BasePipeline(feature=feature, 
                            target=target, 
                            model=model, 
                            metric=median_absolute_relative_error)
                            
    pipeline.fit(config, ticker_list)
    pipeline.export_core('models_data/marketcap_diff') 