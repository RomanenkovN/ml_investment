import argparse
from ml_investment.data import SF1Data
from ml_investment.download import QuandlDownloader
from ml_investment.utils import load_json, save_json

quandl_commodities_codes = ['LBMA/GOLD',
                            'LBMA/SILVER',
                            'JOHNMATT/PALL',
                            'LME/PR_AL',
                            'LME/PR_CU',  
                            'LME/PR_NI',
                            'LME/PR_FM',
                            'ODA/PBARL_USD',
                            'TFGRAIN/CORN', 
                            'ODA/PRICENPQ_USD',  
                            'WORLDBANK/WLD_SOYBEAN_OIL',
                            'CHRIS/CME_DA1',
                            'ODA/PBEEF_USD',
                            '', 
                            '',  
                            '',
                            '',
                            '',
                            '', 
                           ]



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('--config_path', type=str)
    arg('--secrets_path', type=str)
    args = parser.parse_args()
    
    config = load_json(args.config_path)
    secrets = load_json(args.secrets_path)  

    downloader = QuandlDownloader(config, secrets, sleep_time=0.8)

    for code in quandl_commodities_codes:
        downloader.single_download('datasets/{}'.format(code),
                                   '{}/{}.json'.format(config['commodities_data_path'],
                                                  code.replace('/', '_')))
    