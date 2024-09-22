import json
import csv
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse, parse_qs

from configs import CSV_DIR, CSV_BASE, TI_API_KEY, TI_API_URL, logger


# 헤더에 API 키 포함
headers = {
    'X-OTX-API-KEY': TI_API_KEY,
    'Content-Type': 'application/json'
}

def make_csv_file(results=[]):
    today = get_today()
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    csv_filename = f'{CSV_BASE}_{today}.csv'
    csv_header = ['id', 'modified', 'name', 'adversary', 'indicator', 'type', 'malware_families']
    make_csv_from_data(csv_filename, data=csv_header)

    new_results = []

    for result in results:
        indicators = result['indicators']
        modified = result['modified'].split('.')[0]+'z'
        if yesterday in modified:
            new_results.append(result)
            for indicator in indicators:
                new_result = [result['id'], modified, result['name'], result['adversary'], 
                    indicator['indicator'].replace('.', '[.]'), indicator['type'], result['malware_families']] 
                make_csv_from_data(csv_filename, data=new_result)
    return new_results, csv_filename

def make_csv_from_data(csv_filename, data=[]):
    with open(CSV_DIR + '/' + csv_filename, 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

def get_results_from_otx():
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
