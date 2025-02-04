#!/usr/bin/env python
# coding=utf-8
import csv
import time
import gitlab
import collections
import pandas as pd
import openai
import requests

YOUR_GITLAB_TOKEN = ''
PROJECT_ID = ''
GITLAB_API_URL = f'https://gitlab.com/api/v4/projects/{PROJECT_ID}/repository/commits'

headers = {'Authorization': f'Bearer {YOUR_GITLAB_TOKEN}'}

data = pd.read_csv('gitlab_commits.csv')

texts = data['Message'] + "" + data['Author Name']

prompt = "Read the data and analyse what work each person did, the data is as follows：" + texts.str.cat(sep='\n')

system_intel = " answer my questions as if you were an expert in the field."
# 调用GPT-4 API的函数
def ask_GPT4(system_intel, prompt):
    result = openai.ChatCompletion.create(model="gpt-4-0125-preview",
                                 messages=[{"role": "system", "content": system_intel},
                                           {"role": "user", "content": prompt}])
    # 定义文件名和要写入的文本
    file_name = "GPT_simpleanalysis.txt"
    text_to_write = result['choices'][0]['message']['content']

    # 打开文件用于写入（'w'模式）
    # 如果文件已存在，它将被覆盖
    with open(file_name, 'w') as file:
        file.write(text_to_write)
    # 文件会在with语句结束时自动关闭


def fetch_commits():
    """获取项目的所有提交"""
    page = 1
    all_commits = []
    while True:
        params = {'page': page, 'per_page': 100}  # API每页最多返回100项
        response = requests.get(GITLAB_API_URL, headers=headers, params=params)
        commits = response.json()
        if not commits:
            break
        all_commits.extend(commits)
        page += 1
    return all_commits

def fetch_commit_stats(commit_id):
    """获取单个提交的统计数据"""
    url = f"{GITLAB_API_URL}/{commit_id}"
    response = requests.get(f"{url}", headers=headers)
    commit_data = response.json()
    return commit_data.get('stats', {})

def main():
    commit_contributions = {}

    commits = fetch_commits()
    for commit in commits:
        author_name = commit['author_name']
        commit_id = commit['id']
        stats = fetch_commit_stats(commit_id)
        if author_name not in commit_contributions:
            commit_contributions[author_name] = {'additions': 0, 'deletions': 0}
        commit_contributions[author_name]['additions'] += stats.get('additions', 0)
        commit_contributions[author_name]['deletions'] += stats.get('deletions', 0)

    # 打印每个贡献者的添加和删除行数
    for author, stats in commit_contributions.items():
        print(f"{author}: {stats['additions']} additions, {stats['deletions']} deletions")


