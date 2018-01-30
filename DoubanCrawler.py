# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import codecs
import csv
# 导入第三方文件
import expanddouban


def getMovieUrl(category,location):
    """
    该函数用于获取豆瓣电影对应类型和地区的URL
    :param category:豆瓣电影的电影类型：剧情、爱情、喜剧...
    :param location:豆瓣电影的电影所属地区：美国、中国...
    :return :返回豆瓣电影对应类型和地区的URL
    """
    url = "https://movie.douban.com/tag/#/?sort=S&range=9,10&tags=电影,{},{}".format(category,location)
    return url


class Movie(object):
    """电影类，包含以下成员变量"""
    def __init__(self,name, rate, category, location, info_link, cover_link):
        # 电影名称
        self.name = name
        # 电影评分
        self.rate = rate
        # 电影类型
        self.category = category
        # 电影地区
        self.location = location
        # 电影页面链接
        self.info_link = info_link
        # 电影海报图片链接
        self.cover_link = cover_link


def getMovies(category, location):
    """
    构造每一部电影的完整信息，并返回一个存储了每一部电影的列表
    :param category:电影类型的列表
    :param localtion:电影地区的列表
    """
    # 用来存储每一部电影的列表
    movies = []
    # 遍历不同电影类型
    for cat in category:
        # 遍历不同电影地区
        for loc in location:
            # 获取当前条件下已加载的页面html
            html = expanddouban.getHtml(getMovieUrl(cat, loc),True)
            # 创建soup对象
            soup = BeautifulSoup(html,'html.parser')
            # 获取当前条件下每一部电影的信息，recursive=False 表示只获取当前节点的直接子节点
            tags = soup.find(class_='list-wp').find_all('a', recursive=False)
            # 以下循环为获取电影的完整信息，并将其存储到列表中
            for tag in tags:
                # 获取电影的名称
                movie_name = tag.find(class_='title').string
                # 获取电影的评分
                movie_rate = tag.find(class_='rate').string
                # 获取电影的类型
                movie_category = cat
                # 获取电影的地区
                movie_location = loc
                # 获取电影的链接
                movie_info_link = tag.get('href')
                # 获取电影的海报链接
                movie_cover_link = tag.find('img').get('src')
                # 将电影的完整信息存储到列表中
                movies.append([movie_name, movie_rate, movie_category, movie_location, movie_info_link, movie_cover_link])
    # 返回存储电影完整信息的列表
    return movies


# 创建喜欢的电影类型列表
category_list = ['科幻', '动作', '战争']
# 创建喜欢的电影地区列表
location_list = ['大陆', '美国', '香港','台湾','日本','韩国','英国',
'法国','德国','意大利','西班牙','印度','泰国','俄罗斯','伊朗','加拿大',
'澳大利亚','爱尔兰','瑞典','巴西','丹麦']
# 获取当前情况下，所有电影组成的列表
movies_list = getMovies(category_list,location_list)
# 将每一部电影信息，写入文件
# codecs 用于按指定编码进行编码后写入，否则windows打开文件可能出现乱码
with codecs.open('movies.csv', 'w', 'utf_8_sig') as f:
    writer = csv.writer(f)
    for movies in movies_list:
        # 每个电影占一行
        writer.writerow(movies)


# 打开文件，并将每一部电影存储在一个列表中
with open('movies.csv', 'r') as f:
    reader = csv.reader(f)
    movies_csv = list(reader)


def percentage(same_loc_sum, same_cat_sum):
    """
    计算同一地区不同类型的电影占当前地区电影总数的百分比
    :param same_loc_sum:同一地区同一类型电影总数
    :param same_cat_sum:同一地区电影总数
    :return :返回 同一地区不同类型的电影占当前地区电影总数的百分比
    """
    percentage = '%.2f%%' % (same_loc_sum / same_cat_sum * 100)
    return percentage

# 写入文件：每个电影类别中，数量排名前三的地区有哪些，以及分别占此类别电影总数的百分比
# codecs 用于按指定编码进行编码后写入，否则windows打开文件可能出现乱码
with codecs.open('output.txt', 'w', 'utf_8_sig') as f:
    # 输出时使用的字符串
    message = "{}电影排名前三的地区是{}、{}、{}，分别占此类别电影总数的{}%、{}%、{}%。\n"
    # 遍历电影类别
    for cat in category_list:
        # 创建用于存储同一类别 同一地区的电影所属地区和数量 的列表
        same_cat_loc = []
        # 用于存储同一类型的电影总数量
        same_cat_sum = 0
        # 遍历电影地区
        for loc in location_list:
            # 用于存储同一地区同一类型的电影总数
            same_loc_sum = 0
            # 遍历电影列表
            for movie in movies_csv:
                if movie[2] == cat and movie[3] == loc:
                    same_loc_sum += 1
                    same_cat_sum += 1
            # 将电影的地区 和 该地区的电影数量，以元组的形式 存储在列表中
            same_cat_loc.append((loc,same_loc_sum))
            # 使用sorted()方法，使得列表内的元组，按count从小到大的顺序排序
            same_cat_loc = sorted(same_cat_loc, key=lambda x:x[1], reverse=True)

        # 创建列表，用于保存 同一类型同一地区的电影 占 当前类型所有电影的百分比
        cat_loc_per = []
        # 计算同一类型同一地区的电影 占 当前类型所有电影的百分比
        for i in range(len(same_cat_loc)):
            cat_loc_per.append(percentage(same_cat_loc[i][1], same_cat_sum))

        # 输出每个电影类别中，数量排名前三的地区有哪些，以及分别占此类别电影总数的百分比
        print(message.format(cat, same_cat_loc[0][0], same_cat_loc[1][0], same_cat_loc[2][0], cat_loc_per[0], cat_loc_per[1], cat_loc_per[2]))
        # 写入文件
        f.write(message.format(cat, same_cat_loc[0][0], same_cat_loc[1][0], same_cat_loc[2][0], cat_loc_per[0], cat_loc_per[1], cat_loc_per[2]))






