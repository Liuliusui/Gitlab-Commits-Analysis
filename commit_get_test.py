import requests
import csv

ACCESS_TOKEN = ''
REPO_ID = ''
def getcommits():
    # 设置你的访问令牌、仓库ID和API基础URL


    BASE_URL = f"https://gitlab.com/api/v4/projects/{REPO_ID}"
    # 设置请求头
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    # CSV文件名
    csv_filename = 'gitlab_commits.csv'

    # 初始化分页参数
    page = 1
    per_page = 20  # 调整每页的提交数以平衡API请求和性能

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # 写入CSV文件头
        csv_writer.writerow(['Commit SHA', 'Title', 'Author Name', 'Date', 'Message'])

        while True:
            commits_url = f"{BASE_URL}/repository/commits?page={page}&per_page={per_page}"
            response = requests.get(commits_url, headers=headers)

            if response.status_code == 200:
                commits = response.json()
                if not commits:
                    break

                for commit in commits:
                    commit_sha = commit['id']
                    title = commit['title']
                    author_name = commit['author_name']
                    date = commit['created_at']
                    message = commit['message']

                    # Write each submission to a CSV file
                    csv_writer.writerow([commit_sha, title, author_name, date, message])

                page += 1  # 准备请求下一页
            else:
                print("Failed to obtain submission information, status code:", response.status_code)
                break

    print(f"所有提交信息已存入 {csv_filename}")
