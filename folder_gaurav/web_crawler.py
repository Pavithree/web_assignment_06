from bs4 import BeautifulSoup
import requests
from collections import Counter
import matplotlib.pyplot as plt
import logging
import numpy as np
import sys

external_links_dict = dict()
internal_links_dict = dict()
internal_counter_dict = dict()
external_counter_dict = dict()

def external_links(url, flag, link):
    if flag == True:
        if url not in external_links_dict:
            external_links_dict[url] = 1
        else:
            external_links_dict[url] += 1
    else:
        if link in external_counter_dict:
            external_counter_dict[link] += 1
        else:
            external_counter_dict[link] = 1


def internal_links(url, flag, link):
    if flag == True:
        if url not in internal_links_dict:
            internal_links_dict[url] = 1
        else:
            internal_links_dict[url] += 1
    else:
        if link in internal_counter_dict:
            internal_counter_dict[link] += 1
        else:
            internal_counter_dict[link] = 1

def fetch_anchor_tags(tags, flag,link):
    print('Main Link:', link)
    logging.basicConfig(level=logging.INFO, filename='web_crawler.log', filemode='w')
    logging.info('Main Link: {link}'.format(link=link))
    for tag in tags:
        url = tag.get('href', None)
        print('Sub Link:', url)
        logging.info('Sub Link: {count}'.format(count=url))

        if url != None and url.lstrip().startswith('http'):
            external_links(url, flag, link)
        else:
            internal_links(url, flag, link)

def fetch_internal_anchor_tags(tags, flag, link):
    print('Main Link:', link)
    logging.basicConfig(level=logging.INFO, filename='web_crawler.log', filemode='w')
    logging.info('Main Link: {link}'.format(link=link))
    for tag in tags:
        url = tag.get('href', None)
        print('Sub Link:', url)
        logging.info('Sub Link: {count}'.format(count=url))

        if url != None and url.lstrip().startswith('http'):
            external_links(url, flag, link)
        elif url != None and not url.lstrip().startswith('http'):
            internal_links(url, flag, link)


def internal_links_crawl(dict):
    count = 0
    for key, value in dict.items():
        if count < 50:
            if key != None and not key.lstrip().startswith('http') and key.lstrip().startswith('/'):
                url = 'http://localhost:8080' + key
            elif key != None and not key.lstrip().startswith('http') and key.lstrip().startswith('#'):
                url = 'http://localhost:8080/wikipedia_en_simple_all_nopic_2020-10/A/COVID-19_pandemic' + key
            elif key != None and not key.lstrip().startswith('http'):
                url = 'http://localhost:8080/wikipedia_en_simple_all_nopic_2020-10/A/' + key
            # print('Url:', url)
            try:
                new_url = requests.get(url, timeout=10)
            except requests.exceptions.Timeout as e:
                new_url.close()

            html = new_url.content
            soup = BeautifulSoup(html, "html.parser")
            # Retrieve all of the anchor tags
            tags = soup('a')
            fetch_internal_anchor_tags(tags, False, url)

        count += 1

def calculate_total_crawl():
    crawl_count = 0
    for ele in list(internal_counter_dict.values()):
        crawl_count += ele

    for ele in list(external_counter_dict.values()):
        crawl_count += ele

    print('Total number of links that you fetched in the complete process of crawling:', crawl_count + len(external_links_dict) + len(internal_links_dict))

    logging.basicConfig(level=logging.INFO, filename='web_crawler.log', filemode='w')
    logging.info('Total number of links that you fetched in the complete process of crawling: {count}'.format(count=crawl_count + len(external_links_dict) + len(internal_links_dict)))


def plot_parent_links_top_ten(links_dict,msg,img,text):
    sorted_links = Counter(links_dict).most_common(10)
    sorted_links_dict = dict()
    print(msg)
    logging.info(msg)

    for ele in sorted_links:
        print(ele[0], " :", ele[1], " ")
        logging.info('{link} : {frequency}'.format(link=ele[0], frequency=ele[1]))
        sorted_links_dict[ele[0]] = ele[1]

    # Plotting the words to its frequency bar graph
    ext_keys = sorted_links_dict.keys()
    ext_values = sorted_links_dict.values()
    # print('dict:',sorted_links_dict)
    plt.bar(ext_keys, ext_values, alpha=0.2)
    plt.xlabel("List of Links")
    plt.ylabel("Frequency of links")
    plt.title(text+" Links vs Frequency")
    plt.xticks(rotation=90)
    plt.legend(labels=['Frequecy of links'])
    plt.savefig(img, dpi=400)
    # plt.show()

def plot_children_links_frequency(counter_dict,image,text):
    print("The Mean is "+str(np.mean(list(counter_dict.values())))+" and Standard deviation is "+str(np.std(list(counter_dict.values())))+' of '+text+' Links')
    logging.info('The Mean is {mean} and Standard deviation is {std} of {text} Links'.format(mean=str(np.mean(list(counter_dict.values()))), std=str(np.std(list(counter_dict.values()))), text=text))
    # Plotting the words to its frequency bar graph
    int_keys = counter_dict.keys()
    int_values = counter_dict.values()
    f, ax = plt.subplots(figsize=(18, 8))
    plt.bar(int_keys, int_values, alpha=0.2)
    plt.xlabel("List of 50 Links in Parent page")
    plt.ylabel("Frequency of links in Children Pages")
    plt.title("The Mean is "+str(np.mean(list(int_values)))+" and Standard deviation is "+str(np.std(list(int_values)))+' of '+text+' Links')
    plt.xticks(rotation=90)
    plt.legend(labels=['Frequecy of links in Children Pages'])
    plt.savefig(image, dpi=400)
    # plt.show()


def web_crawler(url):
    url = url

    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")

    # Retrieve all of the anchor tags
    tags = soup('a')
    fetch_anchor_tags(tags,True,url)
    internal_links_crawl(internal_links_dict)

    # calculate total number of crawl happened
    calculate_total_crawl()

    int_msg = 'Top 10 Wiki pages that have been linked more than once'
    plot_parent_links_top_ten(internal_links_dict, int_msg, 'internal.png', 'Wiki')

    ext_msg = 'Top 10 external pages (pages with a domain which is not wikipedia_en_simple_all_nopic_2020-10) that have been linked more than once.'
    plot_parent_links_top_ten(external_links_dict, ext_msg, 'external.png', 'External')

    plot_children_links_frequency(internal_counter_dict, 'children_internal.png', 'Internal')

    plot_children_links_frequency(external_counter_dict, 'children_external.png', 'External')



if __name__ == '__main__':
    web_crawler(sys.argv[1])
    # 'http://localhost:8080/wikipedia_en_simple_all_nopic_2020-10/A/COVID-19_pandemic'
