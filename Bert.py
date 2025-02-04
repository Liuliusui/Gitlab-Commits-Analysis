import numpy as np
import openai
import pandas as pd
import seaborn as sns
import umap
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
openai.api_key=""

system_intel = " You're a data analyst"
grouped_data = []

def Bert(k=4):

    # 替换为您的文件路径
    csv_file_path = 'gitlab_commits.csv'

    # 读取CSV文件
    df = pd.read_csv(csv_file_path)
    texts = df['Message']+""+df['Author Name']
            #+ " " + df['Diff'] # 合并标题和描述

    # 将文本转换成向量  Converts text to a vector（The data is divided into 364 dimensions）
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=True)

    # 计算链接矩阵 Computational link matrix
    Z = linkage(embeddings, 'ward')

    # 设置用户自定义的聚类数量

    clusters = fcluster(Z, k, criterion='maxclust')

    reducer = umap.UMAP(random_state=42)
    embedding = reducer.fit_transform(embeddings)

    # 可视化
    plt.figure(figsize=(12, 10))
    plt.scatter(embedding[:, 0], embedding[:, 1], c=clusters, cmap='Spectral', s=5)
    plt.colorbar(boundaries=np.arange(11) - 0.5).set_ticks(np.arange(10))
    plt.title('UMAP projection of the Digits dataset', fontsize=24)
    plt.savefig('UMAP.png', dpi=300)
    plt.show()
    # Draw a tree diagram
    fig, ax = plt.subplots(figsize=(30, 30))
    dendrogram(Z, orientation='right', labels=df['Author Name'].values+""+df['Message'].values, leaf_font_size=8)

    # Draws a horizontal line at the specified distance
    max_d = Z[-(k-1), 2]
    plt.axvline(x=max_d, color='k', linestyle='--')

    plt.title('Hierarchical Clustering Dendrogram with ' + str(k) + ' Clusters')
    plt.xlabel('Distance')
    plt.savefig('Dendrogram_with_clusters.png', dpi=300)
    plt.show()

    # Saves the grouped data to the list
    global grouped_data
    for i in range(1, k+1):
        group = (df['Author Name'][clusters == i]+df['Message'][clusters == i]).tolist()

        grouped_data.append(group)


    print(grouped_data)

    # grouped_data 现在包含了分组数据，每个子列表是一个聚类





    # Calculate the cosine similarity matrix
    similarity_matrix = cosine_similarity(embeddings)
    #
    # # Create a Heatmap label
    labels = [f'{i} {title}' for i, title in enumerate(df['Message']+""+df['Author Name'], 1)]
    #
    # # Set canvas size
    plt.figure(figsize=(35, 35))
    #
    # # Creates a mask to hide the top triangle of the heat map
    mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
    #
    # # Draw a Heatmap
    ax = sns.heatmap(similarity_matrix, mask=mask, xticklabels=labels, yticklabels=labels, cmap='RdBu_r')
    ax.set_title('Text Similarity Heatmap')
    #
    # Place the axis label above and to the left
    #ax.xaxis.tick_top()  # Move the X-axis label to the top

    plt.xticks(rotation=90)  # Rotate the X-axis label to avoid overlap

    ax.yaxis.tick_left()  # Make sure the Y-axis label is on the left
    # Save the image file to the current folder
    plt.savefig('BERT_HeatMap.png', dpi=300)

    plt.show()
    print("If If you think the number of clusters is wrong, you can change it")





# prompt = "This is a cluster of gitlab submissions after clustering, each cluster means a function and I need you to carefully analyze the number of clusters and then what did everyone do in each cluster:" + data_json
# 调用GPT-4 API的函数

def ask_GPT4(system_intel, prompt):

    result = openai.ChatCompletion.create(model="gpt-4-0125-preview",
                                 messages=[{"role": "system", "content": system_intel},
                                           {"role": "user", "content": prompt}])
    # 定义文件名和要写入的文本
    file_name = "GPT_analysis.txt"
    text_to_write = result['choices'][0]['message']['content']

    # 打开文件用于写入（'w'模式）
    # 如果文件已存在，它将被覆盖
    with open(file_name, 'a+') as file:
        file.write(text_to_write)
    # 文件会在with语句结束时自动关闭

def Bert_askGpt4(k):
    file_name = "GPT_analysis.txt"
    with open(file_name, 'w') as file:
        file.write("GPT Analysise")
    for i in range(0,k):
        data_json=str(grouped_data[i])
        print(data_json)
        prompt="What I am giving you now is a cluster, and I need you to do a simple analysis of what's in there for me：" + data_json
        ask_GPT4(system_intel,prompt)
