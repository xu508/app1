import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter

# 设置matplotlib字体，以便正确显示中文
font = FontProperties(fname=r"c:\windows\fonts\msyh.ttc", size=14)  # Windows系统下的Microsoft YaHei字体路径
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置字体为Microsoft YaHei
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# 创建词云图
def create_wordcloud(words, font):
    wordcloud = WordCloud(font_path='simhei.ttf', width=800, height=400).generate(' '.join(words))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# 创建柱状图
def create_bar_chart(data, font):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x='词语', y='频率', data=data, palette="viridis")
    ax.set_xlabel("词语", fontproperties=font)
    ax.set_ylabel("频率", fontproperties=font)
    ax.set_title("词频柱状图", fontproperties=font)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontproperties=font)
    return fig

# 创建饼图
def create_pie_chart(data, font):
    if '词语' not in data.columns:
        raise ValueError("DataFrame must have a '词语' column")
    labels = data['词语']
    sizes = data['频率'].astype(float)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title("词频饼图", fontproperties=font)
    ax.axis('equal')
    return fig

# 创建折线图
def create_line_chart(data, font):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['词语'], data['频率'], marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
    ax.set_xlabel("词语", fontproperties=font)
    ax.set_ylabel("频率", fontproperties=font)
    ax.set_title("词频折线图", fontproperties=font)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontproperties=font)
    return fig

# 创建热力图
def create_heatmap(data, font):
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data, annot=True, cmap="coolwarm", cbar=True, ax=ax)
    ax.set_title("热力图", fontproperties=font)
    return fig

# 创建散点图
def create_scatter_plot(data, font):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(data['词语'], data['频率'], color='r')
    ax.set_xlabel("词语", fontproperties=font)
    ax.set_ylabel("频率", fontproperties=font)
    ax.set_title("词频散点图", fontproperties=font)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontproperties=font)
    return fig

# 创建条形图
def create_horizontal_bar_chart(data, font):
    if '词语' not in data.columns:
        raise ValueError("DataFrame must have a '词语' column")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='频率', y='词语', data=data, palette="muted", orient="h")
    ax.set_xlabel("频率", fontproperties=font)
    ax.set_ylabel("词语", fontproperties=font)
    ax.set_title("词频条形图", fontproperties=font)
    return fig

# 主函数
def main():
    st.title("词频分析")
    url = st.text_input("请输入URL:")
    if url:
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article', class_='article', id='mp-editor')
        article_content = article.get_text(separator="\n", strip=True) if article else "No article found"
        st.write("### 全文展示")
        st.text_area("全文展示", value=article_content, height=300)
        words = jieba.cut(article_content)
        filtered_words = [word for word in words if len(word) > 1 and word.strip() not in ['\n', ' ', '。', ',', '，', '！', '：', '；', '(', ')', '“', '”']]
        word_freq_counts = Counter(filtered_words)
        word_freq_df = pd.DataFrame(list(word_freq_counts.items()), columns=['词语', '频率']).sort_values(by='频率', ascending=False)
        top_20_word_freq_df = pd.DataFrame(list(word_freq_counts.most_common(20)), columns=['词语', '频率'])
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 词频统计结果")
            st.dataframe(word_freq_df)
        with col2:
            st.write("### 词频最高20统计结果")
            st.dataframe(top_20_word_freq_df)

        chart_type = st.selectbox(
            "选择图形类型",
            ["词云图", "柱状图", "饼图", "折线图", "热力图", "散点图", "条形图"]
        )
        top_n = st.slider("选择显示的词频数量", min_value=1, max_value=len(word_freq_df), value=20, step=1)

        if top_n > 0:
            top_n_word_freq_df = word_freq_df.head(top_n)
            if chart_type == "词云图":
                st.write("### 词云图")
                fig = create_wordcloud(top_n_word_freq_df['词语'].tolist(), font)
                st.pyplot(fig)
            elif chart_type == "柱状图":
                st.write("### 柱状图")
                fig = create_bar_chart(top_n_word_freq_df, font)
                st.pyplot(fig)
            elif chart_type == "饼图":
                st.write("### 词频饼图")
                fig = create_pie_chart(top_n_word_freq_df, font)
                st.pyplot(fig)
            elif chart_type == "折线图":
                st.write("### 折线图")
                fig = create_line_chart(top_n_word_freq_df, font)
                st.pyplot(fig)
            elif chart_type == "热力图":
                st.write("### 热力图")
                fig = create_heatmap(top_n_word_freq_df.set_index('词语').T, font)
                st.pyplot(fig)
            elif chart_type == "散点图":
                st.write("### 散点图")
                fig = create_scatter_plot(top_n_word_freq_df, font)
                st.pyplot(fig)
            elif chart_type == "条形图":
                st.write("### 条形图")
                fig = create_horizontal_bar_chart(top_n_word_freq_df, font)
                st.pyplot(fig)

if __name__ == "__main__":
    main()