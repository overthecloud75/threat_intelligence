from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
import requests
import time

from configs import LLM_URL, LLM_MODEL, logger


headers = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json'
}

def summarize_with_langchain(text):
    try:
        prompt = PromptTemplate.from_template(
            "Without line break and key points, Please summarize the following text: {text}"
            "\n\n"
            "Summary:"
        )
        llm = ChatOllama(model=LLM_MODEL, verbose=True)
        runnable = prompt | llm | StrOutputParser()
        response = runnable.invoke({'text': text})
        response = response.replace('\n', '')

        prompt = PromptTemplate.from_template(
            "Without explanation and line break, translate the following text into Korean: {text}"
        )
        runnable = prompt | llm | StrOutputParser()
        response = runnable.invoke({'text': response})
        response = response.replace('\n', '')
        return response
    except Exception as e:
        logger.error(e)
        return ''

def summarize_with_bare_api(text):
    try:
        prompt = 'Without line break and key points, Please summarize the following text: {}' \
            '\n\n' \
            'Summary:'.format(text)
        response = get_from_ollama(prompt)
        if response:
            prompt = 'Without explanation and line break, translate the following text into Korean: {}'.format(response)
            response = get_from_ollama(prompt)
            logger.info(response)
        return response

    except Exception as e:
        logger.error(e)
        return ''

def get_from_ollama(prompt):
    timestamp = time.time()
    data = {'model': LLM_MODEL, 'prompt': prompt, 'stream': False}
    response = requests.post(LLM_URL, json=data, headers=headers)
    logger.info(f"LMM resposne_time: {round(time.time() - timestamp, 2)}")
    # 응답 데이터 처리
    if response.status_code == 200:
        result = response.json()['response']
        return result.replace('\n', '')
    else:
        logger.error(f"Failed to fetch data: {response.status_code}")
        logger.error(response.text)
        return ''

if __name__ == '__main__':
    text = "Cisco Talos has uncovered a campaign employing a new malware family called 'MoonPeak,' a remote access trojan actively developed by a North Korean advanced persistent threat group tracked as 'UAT-5394.' The analysis reveals the evolution of MoonPeak from an open-source malware called XenoRAT, with the threat actors introducing modifications to evade detection and analysis. Talos mapped the infrastructure used in this campaign, including command and control servers, payload hosting sites, and virtual machines for testing implants, unveiling the tactics, techniques, and procedures employed by UAT-5394."
    summarize_with_bare_api(text)