import json
import csv
from datetime import datetime, timedelta
import requests
import copy
from urllib.parse import urlparse, parse_qs
import pymongo

from .ai import summarize_with_bare_api
from .db import post_description_to_db, post_indicator_to_db
from configs import PRODUCTION_MODE, CSV_DIR, CSV_BASE, TI_API_KEY, TI_API_URL, logger


# 헤더에 API 키 포함
headers = {
    'X-OTX-API-KEY': TI_API_KEY,
    'Content-Type': 'application/json'
}

def make_csv_file_save_to_db(results=[]):
    today = get_today()
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    csv_filename = f'{CSV_BASE}_{today}.csv'
    csv_header = ['id', 'modified', 'name', 'adversary', 'indicator', 'type', 'malware_families']
    make_csv_from_data(csv_filename, data=csv_header)

    description_results = []

    i = 0 
    for result in results:
        if not PRODUCTION_MODE and i > 0:
            # dev test를 위해서 설정 
            break
        created = result['created'].split('.')[0]+'z'
        modified = result['modified'].split('.')[0]+'z'
        indicators = result['indicators']
        if yesterday in modified:
            for indicator in indicators:
                if result['malware_families']:
                    malware_family = result['malware_families'][0]
                else:
                    malware_family = ''

                if result['references']:
                    reference = result['references'][0]
                else:
                    reference = ''
                
                # save indicator 
                indicator_result = {'id': result['id'], 'modified': modified, 'name': result['name'], 'adversary': result['adversary'], 
                    'indicator': indicator['indicator'].replace('.', '[.]'), 'type': indicator['type'], 'malware_family': malware_family} 
                make_csv_from_data(csv_filename, data=indicator_result.values())
                post_indicator_to_db(indicator_result)

            # save descroption
            summary = summarize_with_bare_api(result['description'])
            description_result = {'id': result['id'], 'created': created, 'modified': modified, 'name': result['name'], 'description': result['description'], 
                'summary': summary, 'adversary': result['adversary'], 'malware_family': malware_family, 'reference': reference}
            post_description_to_db(description_result) 
            description_results.append(description_result)   
            i = i + 1
    return description_results, csv_filename

def make_csv_from_data(csv_filename, data=[]):
    with open(CSV_DIR + '/' + csv_filename, 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

def get_results_from_ti():
    modified_since = (datetime.utcnow() - timedelta(hours=48)).isoformat() + 'Z'
    params = {
        'modified_since': modified_since,
        'limit': 1000
    }
    # GET 요청 보내기
    response = requests.get(TI_API_URL, headers=headers, params=params)

    # 응답 데이터 처리
    if response.status_code == 200:
        pulses = response.json()
        results = pulses['results']
        return results
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        logger.error(response.text)

def get_today():
    return datetime.today().strftime('%Y-%m-%d')
