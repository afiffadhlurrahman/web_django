from django.shortcuts import render

# from .models import DatasetPublication, HubArticles, Researcher, Topic, Subtopic
from .models import DatasetPublication, Researcher, Topic, Subtopic

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import Substr

from django.core import serializers
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound

from django.db.models import Q
from django.templatetags.static import static
from django import forms

from functools import reduce
import operator
import pandas as pd

import re
import random
import math
from collections import Counter
from datetime import date, datetime

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
ARTICLE_PER_PAGE = 5

# Create your views here.

# t adalah judul dari pencarian-1 dan text adalah judul hasil pencarian-2


def highlight_search(t, text):
    search_list = set(t.split()) & set(text.split())
    for search in list(search_list):
        text = text.replace(
            search, '<span class="highlight">{}</span>'.format(search))
    return text


def topic_view(request):
    mydict = {}
    return render(request, 'topic_view.html', mydict)


def count_total_word_in_title(title, keyword):
    counter = 0
    for key in keyword:
        if key in title:
            counter += 1
    return counter


def func_cosim(text1, text2):
    WORD = re.compile(r"\w+")
    vector1 = Counter(WORD.findall(text1))
    vector2 = Counter(WORD.findall(text2))

    intersection = set(vector1.keys()) & set(vector2.keys())
    numerator = sum([vector1[x] * vector2[x] for x in intersection])

    sum1 = sum([vector1[x] ** 2 for x in list(vector1.keys())])
    sum2 = sum([vector2[x] ** 2 for x in list(vector2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def display_vocab(request):
    # article_all = DatasetPublication.objects.all()

    starttime = datetime.now()
    # keyword_case = ['cekam', 'kentang', 'varietas']
    # keyword_case = ['adsorben', 'selulosa', 'silika']
    # string_keyword = 'cekam, kentang, varietas'
    # cekam, kentang, varietas

    csvfile1 = 'readmysql/static/df_review_django1.csv'
    csvfile2 = 'readmysql/static/keyword_topic_all_updated.csv'

    df_data = pd.read_csv(csvfile1, converters={'nidn': lambda x: str(x)})
    # print(request.GET)
    if 'search' in request.GET:
        query = request.GET.get('search')
        keyword_case = list(query.split(", "))

        frame = pd.read_csv(csvfile2)
        frame = frame.sort_values(by=['df'], ascending=False)
        dict_hasil_search = pd.DataFrame()
        for keyword in keyword_case:
            temp = frame[frame.word.str.contains(
                keyword, regex=False, na=False)][:3]
            dict_hasil_search = pd.concat(
                [dict_hasil_search, temp], ignore_index=True)
        # print(dict_hasil_search)
        endtime1 = datetime.now()
        temp_list = []
        idpub_list_all = []
        for idx1 in dict_hasil_search.index:
            word = dict_hasil_search.word.iloc[idx1]
            num = dict_hasil_search.id_topic.iloc[idx1]

            temp1 = df_data[(df_data['title'].str.contains(word)) & (
                df_data['topic'] == num)]['id_pub'].tolist()
            temp_list.append(temp1)
            idpub_list_all += temp1   # Menggabungkan id_pub menjadi satu list

        dict_hasil_search['id_pub_list'] = temp_list
        endtime2 = datetime.now()

        temp_dict = {}
        for idpub in idpub_list_all:
            title = df_data.loc[df_data['id_pub'] == idpub]['title'].values[0]
            hasil_count = count_total_word_in_title(
                title.split(" "), keyword_case)
            temp_dict[idpub] = hasil_count
        temp_df = pd.DataFrame(list(temp_dict.items()),
                               columns=['id_pub', 'count'])
        # data_source = temp_df['id_pub'].tolist()
        # print(data_source)
        str_keyword = str(keyword_case).replace(
            "[", "").replace("]", "").replace("'", "").replace(", ", " ")
        # count score in percent
        temp_df['score'] = round((temp_df['count'] / 3), 2)

        # select value score > 0.5
        temp_df = temp_df.loc[temp_df['score'] >= 0.5]
        temp_df.reset_index(inplace=True, drop=True)
        if len(temp_df) < 1:
            endtime3 = datetime.now()
            mydict = {
                'checker_msg': 'Data tidak ditemukan!',
                'kata_kunci': str_keyword.replace(" ", ", "),
                'waktu1': endtime1-starttime,
                'waktu2': endtime2-endtime1,
                'waktu3': endtime3-endtime2
            }
            return render(request, 'display_vocab.html', mydict)

        temp_df['title'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].title.item())
        temp_df['topic'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].topic.item())
        temp_df['subtopic'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].subtopic.item())
        temp_df['title_list'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].title_list.item())
        temp_df['topic_name'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].topic_name.item())
        temp_df['subtopic_name'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].subtopic_name.item())
        temp_df['researcher_name'] = temp_df['id_pub'].apply(
            lambda x: df_data.loc[df_data['id_pub'] == x].researcher_name.item())

        endtime3 = datetime.now()

        jumlah_articles = len(temp_df)

        temp_df['sim_score'] = temp_df['title'].apply(
            lambda x: round(func_cosim(x, str_keyword), 3))
        temp_df['sim_score_preprocessing'] = temp_df['title_list'].apply(
            lambda x: round(func_cosim(x, str_keyword), 3))

        # article_list = DatasetPublication.objects.exclude(subtopic__isnull=True).order_by(
        #     Substr('id_pub', 7))[:10]

        endtime4 = datetime.now()

        temp_df = temp_df.sort_values(
            by=['sim_score_preprocessing'], ascending=False).reset_index().drop(columns=['index'])[:10]
        # context = {'DataFrame': temp_df}
        temp_df['title'] = temp_df['title'].str.upper()
        temp_df['sim_score_preprocessing'] = temp_df['sim_score_preprocessing'].map(
            '{:,.3f}'.format)
        mydict = {
            'df': temp_df[:10].to_html(),
            'DataFrame': temp_df[:10],
            'kata_kunci': str_keyword.replace(" ", ", "),
            'jumlah_articles': jumlah_articles,
            'waktu1': endtime1-starttime,
            'waktu2': endtime2-endtime1,
            'waktu3': endtime3-endtime2,
            'waktu4': endtime4-endtime3
        }
        return render(request, 'display_vocab.html', mydict)
    else:
        jumlah_articles = len(df_data)
        df_data = df_data.sort_values(
            by=['id_pub'], ascending=True).reset_index().drop(columns=['index'])[:10]
        endtime = datetime.now()
        df_data['title'] = df_data['title'].str.upper()
        mydict = {
            'df': df_data[:10].to_html(),
            'DataFrame': df_data[:10],
            'jumlah_articles': jumlah_articles,
            'waktu': endtime-starttime
        }
        return render(request, 'display_vocab.html', mydict)


def similar(request, id):
    if 'filtered' in request.POST:
        starttime = datetime.now()

        df_data = pd.read_csv('readmysql/static/df_review_django1.csv',
                              converters={'nidn': lambda x: str(x)})
        df_sim_topic = pd.read_csv(
            'readmysql/static/sim_topic.csv', index_col='Unnamed: 0')
        df_sim_researcher = pd.read_csv(
            'readmysql/static/sim_reseacher.csv', index_col='Unnamed: 0')
        df_sim_subtopic = pd.read_csv(
            'readmysql/static/sim_subtopic.csv', index_col='Unnamed: 0')
        filtered_list = request.POST.getlist('filtered')
        val = 0
        article_id = df_data[df_data['id_pub'] == id].index[0]
        kelas = ''
        endtime1 = datetime.now()
        if len(filtered_list) == 1:
            # skenario 1
            if 'check_topic' in filtered_list:
                val = 1
                dict_val = sken1(article_id, df_data, df_sim_topic)
                kelas = 'Topik'
            # skenario 2
            elif 'check_subtopic' in filtered_list:
                val = 2
                dict_val = sken2(article_id, df_data, df_sim_subtopic)
                kelas = 'Subtopik'
            # skenario 3
            elif 'check_researcher' in filtered_list:
                val = 3
                dict_val = sken3(article_id, df_data, df_sim_researcher)
                kelas = 'Peneliti'
        elif len(filtered_list) == 2:
            # skenario 4
            if ('check_topic' in filtered_list) and ('check_subtopic' in filtered_list):
                val = 4
                dict_val = sken4(article_id, df_data, df_sim_subtopic)
                kelas = 'Topik dan Subtopik'
            # skenario 5
            elif ('check_topic' in filtered_list) and ('check_researcher' in filtered_list):
                val = 5
                dict_val = sken5(article_id, df_data)
                kelas = 'Peneliti dan Topik'
        endtime2 = datetime.now()
        if val > 0:
            if val <= 5:
                dict_val = dict_val[:10]
                dict_val['topic_name'] = dict_val['id_pub'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].topic_name.item())
                dict_val['subtopic_name'] = dict_val['id_pub'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].subtopic_name.item())
                dict_val['researcher_name'] = dict_val['id_pub'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].researcher_name.item())

                dict_val['sim_topic_from_name'] = dict_val['sim_idpub_from'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].topic_name.item())
                dict_val['sim_subtopic_from_name'] = dict_val['sim_idpub_from'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].subtopic_name.item())
                dict_val['sim_researcher_from_name'] = dict_val['sim_idpub_from'].apply(
                    lambda x: df_data.loc[df_data['id_pub'] == x].researcher_name.item())

                article_search = dict_val.iloc[0].copy()
                article_search.sim_article_from = article_search.sim_article_from.upper()

                dict_val['title'] = dict_val['title'].str.upper()
                dict_val['sim_score'] = dict_val['sim_score'].map(
                    '{:,.3f}'.format)
                dict_val['title_list'] = dict_val['title_list'].apply(
                    lambda x: highlight_search(article_search['sim_art_str_from'], x))

                endtime3 = datetime.now()
                mydict = {
                    'skenario': val,
                    'df': dict_val.to_html(),
                    'article_search': article_search,
                    'DataFrame': dict_val[:10],
                    'waktu1': endtime1-starttime,
                    'waktu2': endtime2-endtime1,
                    'waktu3': endtime3-endtime2,
                    'kelas': kelas
                }
            else:
                endtime2 = datetime.now()
                mydict = {'skenario': val, 'waktu': endtime1-starttime}

            return render(request, 'similar.html', mydict)
    return HttpResponseNotFound('<h1>Page not found</h1>')


def get_recommendations_sken1(idx, cosine_sim, indices, df_data):
    # Get the pairwsie similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the title based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for 10 most similar title
    sim_scores = sim_scores[1:11]

    # Get the title indices
    title_indices = [i[0] for i in sim_scores]

    # Select title in indices (title as index in Series indices)
    tmp1 = indices[title_indices].index.tolist()

    # Select dpub of article in df_data (real index) as a list
    list_idpub = df_data[df_data['title_list'].isin(tmp1)]['id_pub'].tolist()

    # Return id_pub, title, title_list, topic, and subtopic
    df_return = df_data[df_data['id_pub'].isin(list_idpub)]
    r_idpub, r_title, r_titlelist, r_topic, r_subtopic = df_return['id_pub'], df_return[
        'title'], df_return['title_list'], df_return['topic'], df_return['subtopic']

    # Return the top 10 most similar title
    return r_idpub, r_title, r_titlelist, sim_scores, r_topic, r_subtopic


def find_topic_sim(idx, df_sim_topic):
    idx = 'topic' + str(idx)
    temp = df_sim_topic[idx].sort_values(ascending=False)
    if temp[1:][temp > 0.1].empty:
        return temp[:2]
    else:
        return temp[temp > 0.1]


def sken1(id_article, df_data, df_sim_topic):
    id_title = df_data.iloc[id_article]['title']
    id_pub = df_data.iloc[id_article]['id_pub']
    id_topic = df_data.iloc[id_article]['topic']
    id_title_str = df_data.iloc[id_article]['title_list']

    sim = find_topic_sim(id_topic, df_sim_topic).index.to_series()
    sim = sim.str.replace('topic', '').tolist()
    sim = list(map(int, sim))

    df_test1 = df_data.loc[df_data['topic'].isin(sim)].copy()
    df_test1.reset_index(inplace=True)
    df_test1.drop(columns=['index'], inplace=True)

    df_test11 = df_data.loc[df_data['id_pub'] == id_pub].copy()
    df_test11.reset_index(inplace=True)
    df_test11.drop(columns=['index'], inplace=True)

    indices = pd.Series(
        df_test1.index, index=df_test1['title_list']).drop_duplicates()

    title_article = df_test1['title_list'].copy()
    title_article1 = df_test11['title_list'].copy()

    tfidf = TfidfVectorizer()

    # # Construct the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(title_article)
    tfidf_matrix1 = tfidf.transform(title_article1)

    # # Generate the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix1, tfidf_matrix)

    indeks = 0  # karena di cosine array, judul tsb ada di indeks 0

    hasil_idpub, hasil_title, hasil_title_list, sim_scores, hasil_topic, hasil_subtopic = get_recommendations_sken1(
        indeks, cosine_sim, indices, df_data)
    hasil = hasil_title.to_frame()
    hasil.insert(0, 'id_pub', [i for i in hasil_idpub])

    hasil['title_list'] = [i for i in hasil_title_list]
    hasil['topic'] = [i for i in hasil_topic]
    hasil['subtopic'] = [i for i in hasil_subtopic]
    hasil['sim_score'] = [round(i[1], 3) for i in sim_scores]
    # hasil['sim_score_title'] = [round(func_cosim(id_title, s), 3) for s in hasil['title']]

    hasil['sim_idpub_from'] = [id_pub for i in range(len(sim_scores))]
    hasil['sim_article_from'] = [id_title for i in range(len(sim_scores))]
    hasil['sim_art_str_from'] = [id_title_str for i in range(len(sim_scores))]
    hasil['sim_topic_from'] = [id_topic for i in range(len(sim_scores))]
    return hasil


def get_recommendations_sken2(idx, cosine_sim, indices, df_data):
    # Get the pairwsie similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the title based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for 10 most similar title
    sim_scores = sim_scores[1:11]

    # Get the title indices
    title_indices = [i[0] for i in sim_scores]

    # Select title in indices (title as index in Series indices)
    tmp1 = indices[title_indices].index.tolist()

    # Select dpub of article in df_data (real index) as a list
    list_idpub = df_data[df_data['title_list'].isin(tmp1)]['id_pub'].tolist()

    # Return id_pub, title, title_list, topic, and subtopic
    df_return = df_data[df_data['id_pub'].isin(list_idpub)]
    r_idpub, r_title, r_titlelist, r_topic, r_subtopic = df_return['id_pub'], df_return[
        'title'], df_return['title_list'], df_return['topic'], df_return['subtopic']

    # Return the top 10 most similar title
    return r_idpub, r_title, r_titlelist, sim_scores, r_topic, r_subtopic


def find_subtopic_sim(idx, df_sim_subtopic):
    idx = 'subtopic' + str(idx)
    temp = df_sim_subtopic[idx].sort_values(ascending=False)
    if temp[1:][temp > 0.1].empty:
        return temp[:2]
    else:
        return temp[temp > 0.1]


def sken2(id_article, df_data, df_sim_subtopic):
    id_title = df_data.iloc[id_article]['title']
    id_pub = df_data.iloc[id_article]['id_pub']
    id_topic = df_data.iloc[id_article]['topic']
    id_subtopic = df_data.iloc[id_article]['subtopic']
    id_title_str = df_data.iloc[id_article]['title_list']

    sim = find_subtopic_sim(id_subtopic, df_sim_subtopic).index.to_series()
    sim = sim.str.replace('subtopic', '').tolist()
    sim = list(map(int, sim))  # untuk mengubah str ke int

    df_test1 = df_data.loc[df_data['subtopic'].isin(sim)].copy()
    df_test1.reset_index(inplace=True)
    df_test1.drop(columns=['index'], inplace=True)

    df_test11 = df_data.loc[df_data['id_pub'] == id_pub].copy()
    df_test11.reset_index(inplace=True)
    df_test11.drop(columns=['index'], inplace=True)

    indices = pd.Series(
        df_test1.index, index=df_test1['title_list']).drop_duplicates()

    title_article = df_test1['title_list'].copy()
    title_article1 = df_test11['title_list'].copy()

    tfidf = TfidfVectorizer()

    # Construct the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(title_article)
    tfidf_matrix1 = tfidf.transform(title_article1)

    # Generate the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix1, tfidf_matrix)

    indeks = 0  # karena di cosine array, judul tsb ada di indeks 0
    hasil_idpub, hasil_title, hasil_title_list, sim_scores, hasil_topic, hasil_subtopic = get_recommendations_sken2(
        indeks, cosine_sim, indices, df_data)
    hasil = hasil_title.to_frame()
    hasil.insert(0, 'id_pub', [i for i in hasil_idpub])

    hasil['title_list'] = [i for i in hasil_title_list]
    hasil['topic'] = [i for i in hasil_topic]
    hasil['subtopic'] = [i for i in hasil_subtopic]

    hasil['sim_score'] = [round(i[1], 3) for i in sim_scores]
    hasil['sim_idpub_from'] = [id_pub for i in range(len(sim_scores))]
    hasil['sim_article_from'] = [id_title for i in range(len(sim_scores))]
    hasil['sim_art_str_from'] = [id_title_str for i in range(len(sim_scores))]
    hasil['sim_subtopic_from'] = [id_subtopic for i in range(len(sim_scores))]

    return hasil


def get_recommendations_sken3(idx, cosine_sim, indices, df_data):
    # Get the pairwsie similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the title based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for 10 most similar title
    sim_scores = sim_scores[1:11]

    # Get the title indices
    title_indices = [i[0] for i in sim_scores]

    # Select title in indices (title as index in Series indices)
    tmp1 = indices[title_indices].index.tolist()

    # Select dpub of article in df_data (real index) as a list
    list_idpub = df_data[df_data['title_list'].isin(tmp1)]['id_pub'].tolist()

    # Return id_pub, title, title_list, topic, and subtopic
    df_return = df_data[df_data['id_pub'].isin(list_idpub)]
    r_idpub, r_title, r_titlelist, r_topic, r_subtopic, r_nidn = df_return['id_pub'], df_return[
        'title'], df_return['title_list'], df_return['topic'], df_return['subtopic'], df_return['nidn']

    # Return the top 10 most similar title
    return r_idpub, r_title, r_titlelist, sim_scores, r_topic, r_subtopic, r_nidn


def find_researcher_sim(idx, df_sim_researcher):
    temp = df_sim_researcher[idx].sort_values(ascending=False)
    if temp[1:][temp > 0.2].empty:  # jika similarity selain dg nidn input tdk ada yang lebih dari 0.2
        return temp[:2]  # return nidn inputan dan top 1 selain inputan
    else:
        return temp[temp > 0.2]


def sken3(id_article, df_data, df_sim_researcher):
    id_title = df_data.iloc[id_article]['title']
    id_title_str = df_data.iloc[id_article]['title_list']
    id_pub = df_data.iloc[id_article]['id_pub']
    id_topic = df_data.iloc[id_article]['topic']
    id_subtopic = df_data.iloc[id_article]['subtopic']
    # ambil nidn berdasarkan id_pub
    id_researcher = df_data[df_data['id_pub'] == id_pub]['nidn'].iloc[0]

    # print(idx, id_pub, id_topic, id_subtopic, id_researcher)

    # handle untuk researcher yg tidak memiliki keyword
    try:
        sim = find_researcher_sim(
            id_researcher, df_sim_researcher).index.to_series()
        sim = sim.tolist()
    except:
        print("Researcher ", id_researcher, " do not have keywords.")
    finally:
        sim = [id_researcher]

    df_test1 = df_data.loc[df_data['nidn'].isin(sim)].copy()
    df_test1.reset_index(inplace=True)
    df_test1.drop(columns=['index'], inplace=True)

    df_test11 = df_data.loc[df_data['id_pub'] == id_pub].copy()
    df_test11.reset_index(inplace=True)
    df_test11.drop(columns=['index'], inplace=True)

    indices = pd.Series(
        df_test1.index, index=df_test1['title_list']).drop_duplicates()

    title_article = df_test1['title_list'].copy()
    title_article1 = df_test11['title_list'].copy()

    tfidf = TfidfVectorizer()

    # Construct the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(title_article)
    tfidf_matrix1 = tfidf.transform(title_article1)

    # Generate the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix1, tfidf_matrix)

    indeks = 0  # karena di cosine array, judul tsb ada di indeks 0
    hasil_idpub, hasil_title, hasil_title_list, sim_scores, hasil_topic, hasil_subtopic, hasil_nidn = get_recommendations_sken3(
        indeks, cosine_sim, indices, df_data)

    hasil = hasil_title.to_frame()
    hasil.insert(0, 'id_pub', [i for i in hasil_idpub])

    hasil['topic'] = [i for i in hasil_topic]
    hasil['subtopic'] = [i for i in hasil_subtopic]
    hasil['nidn'] = [i for i in hasil_nidn]

    hasil['sim_score'] = [round(i[1], 3) for i in sim_scores]
    hasil['sim_idpub_from'] = [id_pub for i in range(len(sim_scores))]
    hasil['sim_article_from'] = [id_title for i in range(len(sim_scores))]
    hasil['sim_art_str_from'] = [id_title_str for i in range(len(sim_scores))]
    hasil['sim_topic_from'] = [id_topic for i in range(len(sim_scores))]
    hasil['sim_nidn_from'] = [id_researcher for i in range(len(sim_scores))]

    hasil['title_list'] = [i for i in hasil_title_list]

    return hasil


def get_recommendations_sken4(idx, cosine_sim, indices, df_data):
    # Get the pairwsie similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the title based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for 10 most similar title
    sim_scores = sim_scores[1:11]

    # Get the title indices
    title_indices = [i[0] for i in sim_scores]

    # Select title in indices (title as index in Series indices)
    tmp1 = indices[title_indices].index.tolist()

    # Select dpub of article in df_data (real index) as a list
    list_idpub = df_data[df_data['title_list'].isin(tmp1)]['id_pub'].tolist()

    # Return id_pub, title, title_list, topic, and subtopic
    df_return = df_data[df_data['id_pub'].isin(list_idpub)]
    r_idpub, r_title, r_titlelist, r_topic, r_subtopic = df_return['id_pub'], df_return[
        'title'], df_return['title_list'], df_return['topic'], df_return['subtopic']

    # Return the top 10 most similar title
    return r_idpub, r_title, r_titlelist, sim_scores, r_topic, r_subtopic


def find_subtopic_sim_sken4(id_topic, df_sim_subtopic):
    upper, lower = id_topic * 20, (id_topic * 20) - 20
    list_subtopic = []
    for idx in range(lower+1, upper+1):
        idx = 'subtopic' + str(idx)
        temp_series = pd.Series(dtype='object')
        temp = df_sim_subtopic[idx].sort_values(ascending=False)
        temp = temp[temp < 1.0]
        # jika similarity subtopic diatas 0.1 tidak ada, maka ambil top 1 saja dg syarat top 1 != 0
        if temp[temp > 0.1].empty:
            temp_top_1 = temp[:1].values
            # print(temp_top_1)
            if temp_top_1 > 0.0:  # cek apakah top 1 tidak bernilai 0
                temp_series = temp[:1].index.to_series()
                temp_series = temp_series.str.replace('subtopic', '').tolist()
                temp_series = list(map(int, temp_series))
                list_subtopic += temp_series
                # print(idx, temp_series, temp[:1])
        else:
            # display(temp[temp > 0.1])
            temp_series = temp[temp > 0.1].index.to_series()
            temp_series = temp_series.str.replace('subtopic', '').tolist()
            temp_series = list(map(int, temp_series))
            list_subtopic += temp_series
            # print(idx, temp_series, temp[:1])
    # remove duplicate in list subtopic
    list_subtopic = list(set(list_subtopic))
    return list_subtopic


def sken4(id_article, df_data, df_sim_subtopic):
    id_title = df_data.iloc[id_article]['title']
    id_title_str = df_data.iloc[id_article]['title_list']
    id_pub = df_data.iloc[id_article]['id_pub']
    id_topic = df_data.iloc[id_article]['topic']
    id_subtopic = df_data.iloc[id_article]['subtopic']

    upper, lower = id_topic * 20, (id_topic * 20) - 19

    sim = find_subtopic_sim_sken4(id_topic, df_sim_subtopic)
    # menambahkan rentang subtopik dari topik artikel awal
    sim += [i for i in range(lower, upper)]

    # print("INI SIMILARITY SUBTOPIK",sim)
    df_test1 = df_data.loc[df_data['subtopic'].isin(sim)].copy()
    df_test1.reset_index(inplace=True)
    df_test1.drop(columns=['index'], inplace=True)

    df_test11 = df_data.loc[df_data['id_pub'] == id_pub].copy()
    df_test11.reset_index(inplace=True)
    df_test11.drop(columns=['index'], inplace=True)

    indices = pd.Series(
        df_test1.index, index=df_test1['title_list']).drop_duplicates()

    title_article = df_test1['title_list'].copy()
    title_article1 = df_test11['title_list'].copy()

    tfidf = TfidfVectorizer()

    # Construct the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(title_article)
    tfidf_matrix1 = tfidf.transform(title_article1)

    # Generate the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix1, tfidf_matrix)

    indeks = 0  # karena di cosine array, judul tsb ada di indeks 0
    hasil_idpub, hasil_title, hasil_title_list, sim_scores, hasil_topic, hasil_subtopic = get_recommendations_sken4(
        indeks, cosine_sim, indices, df_data)
    hasil = hasil_title.to_frame()
    hasil.insert(0, 'id_pub', [i for i in hasil_idpub])

    hasil['title_list'] = [i for i in hasil_title_list]
    hasil['topic'] = [i for i in hasil_topic]
    hasil['subtopic'] = [i for i in hasil_subtopic]

    hasil['sim_score'] = [round(i[1], 3) for i in sim_scores]
    hasil['sim_idpub_from'] = [id_pub for i in range(len(sim_scores))]
    hasil['sim_article_from'] = [id_title for i in range(len(sim_scores))]
    hasil['sim_art_str_from'] = [id_title_str for i in range(len(sim_scores))]
    hasil['sim_topic_from'] = [id_topic for i in range(len(sim_scores))]
    hasil['sim_subtopic_from'] = [id_subtopic for i in range(len(sim_scores))]

    return hasil


def get_recommendations_sken5(idx, cosine_sim, indices, df_data):
    # Get the pairwsie similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the title based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores for 10 most similar title
    sim_scores = sim_scores[1:11]

    # Get the title indices
    title_indices = [i[0] for i in sim_scores]

    # Select title in indices (title as index in Series indices)
    tmp1 = indices[title_indices].index.tolist()

    # Select dpub of article in df_data (real index) as a list
    list_idpub = df_data[df_data['title_list'].isin(tmp1)]['id_pub'].tolist()

    # Return id_pub, title, title_list, topic, and subtopic
    df_return = df_data[df_data['id_pub'].isin(list_idpub)]
    r_idpub, r_title, r_titlelist, r_topic, r_subtopic, r_nidn = df_return['id_pub'], df_return[
        'title'], df_return['title_list'], df_return['topic'], df_return['subtopic'], df_return['nidn']

    # Return the top 10 most similar title
    return r_idpub, r_title, r_titlelist, sim_scores, r_topic, r_subtopic, r_nidn


# mencari researcher yang memiliki artikel lebih dari 3 pada topik yang sama dengan researcher artikel tsb
def find_researcher_expert_on(nidn, nidn_counter, df_data):
    # mencari semua topik yang memiliki artikel lebih dari 3 pada researcher tsb
    list_topic_focused = nidn_counter[nidn_counter['nidn']
                                      == nidn]['topic'].tolist()
    if len(list_topic_focused) == 0:
        list_topic_focused = top1_topic_researcher(nidn, df_data)
    result_list = []
    for idx in list_topic_focused:
        result_list += nidn_counter[nidn_counter['topic']
                                    == idx]['nidn'].tolist()
    return result_list


# ambil topic dengan artikel terbanyak yang researcher tsb miliki
# jika ada dua atau lebih topik yg sama banyaknya, pilih salah satu secara random
def top1_topic_researcher(nidn, df_data):
    top1 = df_data[df_data['nidn'] == nidn].groupby(['nidn', 'topic']).size(
    ).sort_values(ascending=False).reset_index(name='count')
    top1_count = top1.iloc[0][2]  # row 0, column 2 (kolom count)
    top1 = top1[top1['count'] == top1_count]['topic'].tolist()
    top1 = random.choice(top1)
    return [top1]


def sken5(id_article, df_data):
    nidn_counter = df_data.groupby(['nidn', 'topic']).size(
    ).sort_values(ascending=False).reset_index(name='count')
    nidn_counter = nidn_counter[nidn_counter['count'] > 3]

    id_title = df_data.iloc[id_article]['title']
    id_title_str = df_data.iloc[id_article]['title_list']
    id_pub = df_data.iloc[id_article]['id_pub']
    id_topic = df_data.iloc[id_article]['topic']
    id_subtopic = df_data.iloc[id_article]['subtopic']
    # ambil nidn berdasarkan id_pub
    id_researcher = df_data[df_data['id_pub'] == id_pub]['nidn'].iloc[0]

    # print(idx, id_pub, id_topic, id_subtopic, id_researcher)

    sim = find_researcher_expert_on(id_researcher, nidn_counter, df_data)

    df_test1 = df_data.loc[df_data['nidn'].isin(sim)].copy()
    df_test1.reset_index(inplace=True)
    df_test1.drop(columns=['index'], inplace=True)

    df_test11 = df_data.loc[df_data['id_pub'] == id_pub].copy()
    df_test11.reset_index(inplace=True)
    df_test11.drop(columns=['index'], inplace=True)

    indices = pd.Series(
        df_test1.index, index=df_test1['title_list']).drop_duplicates()

    title_article = df_test1['title_list'].copy()
    title_article1 = df_test11['title_list'].copy()

    tfidf = TfidfVectorizer()

    # display(title_article)

    # Construct the TF-IDF matrix
    tfidf_matrix = tfidf.fit_transform(title_article)
    tfidf_matrix1 = tfidf.transform(title_article1)

    # Generate the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix1, tfidf_matrix)

    indeks = 0  # karena di cosine array, judul tsb ada di indeks 0
    hasil_idpub, hasil_title, hasil_title_list, sim_scores, hasil_topic, hasil_subtopic, hasil_nidn = get_recommendations_sken5(
        indeks, cosine_sim, indices, df_data)
    hasil = hasil_title.to_frame()
    hasil.insert(0, 'id_pub', [i for i in hasil_idpub])

    hasil['title_list'] = [i for i in hasil_title_list]
    hasil['topic'] = [i for i in hasil_topic]
    hasil['subtopic'] = [i for i in hasil_subtopic]
    hasil['nidn'] = [i for i in hasil_nidn]

    hasil['sim_score'] = [round(i[1], 3) for i in sim_scores]
    hasil['sim_idpub_from'] = [id_pub for i in range(len(sim_scores))]
    hasil['sim_article_from'] = [id_title for i in range(len(sim_scores))]
    hasil['sim_art_str_from'] = [id_title_str for i in range(len(sim_scores))]
    hasil['sim_topic_from'] = [id_topic for i in range(len(sim_scores))]
    hasil['sim_nidn_from'] = [id_researcher for i in range(len(sim_scores))]

    return hasil


def recommend(request, id):
    article_search = DatasetPublication.objects.order_by(Substr('id_pub', 7)).get(
        id_pub=id)
    # print(article.id_pub)
    # articles = DatasetPublication.objects.order_by(
    #     Substr('id_pub', 7)).select_related('hub_articles').filter(Q(id_article1=id) | Q(id_article2=id))
    # query = 'SELECT dpub.id_pub, dpub.title, dpub.topic, dpub.subtopic \
    #             FROM hub_articles AS hub, dataset_publication AS dpub \
    #             WHERE hub.id_article2 = dpub.id_pub AND hub.id_article1 = 8788'
    # articles = DatasetPublication.objects.raw(query)
    articles = HubArticles.objects.order_by(
        Substr('id_article2', 7)).filter(id_article1=id)
    print("ini loh", articles)
    for x in articles:
        print(x.id_article1, '\t||\t', x.id_article2)
        print('##############################################')
    return render(request, 'recommend.html', {'id_pub': id, 'article_search': article_search, 'articles': articles})


def index(request):
    articles_query = DatasetPublication.objects.order_by(Substr('id_pub', 7))
    query = ''

    if 'search' in request.GET:
        query = request.GET.get('search')
        query_list = query.split(' ')
        query_set = reduce(operator.and_, (Q(title__icontains=x)
                                           for x in query_list))
        # articles_query = DatasetPublication.objects.filter(query_set)
        articles_query = DatasetPublication.objects.order_by(
            Substr('id_pub', 7)).filter(query_set)

        # query = request.GET.get('search')
        # # query_search = query1 + "WHERE d.title LIKE '%" + str(q) + "%' " + query2
        # articles_query = DatasetPublication.objects.order_by(
        #     Substr('id_pub', 7)).filter(title__icontains=query)

    # Paginition
    page_number = request.GET.get('page', 1)
    if len(articles_query) > 20:
        paginator = Paginator(articles_query, ARTICLE_PER_PAGE)
    elif len(articles_query) > 0 and len(articles_query) < 20:
        paginator = Paginator(articles_query, len(articles_query))

    try:
        articles_obj = paginator.page(page_number)
    except PageNotAnInteger:
        articles_obj = paginator.page(ARTICLE_PER_PAGE)
    except EmptyPage:
        articles_obj = paginator.page(paginator.num_pages)

    # print(query.split(), articles_query.count())

    context = {'articles': articles_obj, 'query': query,
               'total_articles': len(articles_query)}

    return render(request, 'index.html', context)


def load_more(request):
    queryPage = int(request.POST['queryPage'])
    # print(queryPage)
    offset = int(request.POST['offset']) * queryPage

    limit = 5
    query = str(request.POST['query'])
    # articles = DatasetPublication.objects.raw('SELECT * \
    #                                         FROM dataset_publication as d \
    #                                         ORDER BY d.id_pub+ 0 ASC')[offset:limit+offset]
    if len(query) > 0:
        # query_search = query1 + "WHERE d.title LIKE '%" + str(q) + "%' " + query2
        articles = DatasetPublication.objects.order_by(Substr('id_pub', 7)).filter(
            title__icontains=query)[offset:limit+offset]
        totalData = DatasetPublication.objects.order_by(
            Substr('id_pub', 7)).filter(title__icontains=query).count()
    else:
        articles = DatasetPublication.objects.order_by(Substr('id_pub', 7))[
            offset:limit+offset]
        totalData = DatasetPublication.objects.order_by(
            Substr('id_pub', 7)).count()

    # print(query, totalData, offset)

    data = {}
    articles_json = serializers.serialize('json', articles)
    # print(Substr('id_pub',3))
    return JsonResponse(data={'articles': articles_json, 'totalResult': totalData, 'offset': offset})

# SELECT d.id_pub, d.title, t.name as topic, s.name as subtopic
# FROM dataset_publication as d, topic as t, subtopic as s
# WHERE d.topic = t.topic_id and d.subtopic = s.subtopic_id
# ORDER BY d.id_pub+ 0 ASC LIMIT 15


# CREATE TABLE hub_articles (
#     id_hub varchar(25) NOT NULL,
#     id_article1 varchar(25),
#     id_article2 varchar(25),
#     PRIMARY KEY (id_hub));

# ALTER TABLE hub_articles CHANGE id_article1 id_article1 VARCHAR(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;
# ALTER TABLE hub_articles CHANGE id_article2 id_article2 VARCHAR(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL;

# ALTER TABLE hub_articles ADD CONSTRAINT fk_hub_article1 FOREIGN KEY (id_article1) REFERENCES dataset_publication(id_pub) ON DELETE RESTRICT ON UPDATE RESTRICT;
# ALTER TABLE hub_articles ADD CONSTRAINT fk_hub_article2 FOREIGN KEY (id_article2) REFERENCES dataset_publication(id_pub) ON DELETE RESTRICT ON UPDATE RESTRICT;

# INSERT INTO hub_articles(id_hub, id_article1, id_article2) VALUES (1, 8788, 877);
# INSERT INTO hub_articles(id_hub, id_article1, id_article2) VALUES (2, 8788, 8405);
# INSERT INTO hub_articles(id_hub, id_article1, id_article2) VALUES (3, 8788, 26127);
# INSERT INTO hub_articles(id_hub, id_article1, id_article2) VALUES (4, 8788, 26148);
# INSERT INTO hub_articles(id_hub, id_article1, id_article2) VALUES (5, 8788, 91063);
