# EventMonitor
Event monitor based on online news corpus  built by Baidu search enginee using event keyword  for event storyline and analysis，基于给定事件关键词，采集事件资讯，对事件进行挖掘和分析。 
# 项目路线图
 ![image](https://github.com/liuhuanyong/EventMonitor/blob/master/image/project.png)
# 项目细分
# 1)　基于话题关键词的话题历时语料库采集
执行方式：进入EventMonitor目录下，进入cmd窗口，执行"scrapy crawl eventspider -a keyword=话题关键词"，或者直接python crawl.py, 等待数秒后，既可以在news文件夹中存储相应的新闻文件,可以得到相应事件的话题集,话题历史文本  
 ![image](https://github.com/liuhuanyong/EventMonitor/blob/master/image/topic.png)
 ![image](https://github.com/liuhuanyong/EventMonitor/blob/master/image/news.png)
 ![image](https://github.com/liuhuanyong/EventMonitor/blob/master/image/content.png)    
# 2)关于热点事件的情感分析
对于1)得到的历史语料，可以使用基于依存语义和情感词库的篇章级情感分析算法进行情感分析  
这部分参考我的篇章级情感分析项目DocSentimentAnalysis：https://github.com/liuhuanyong/DocSentimentAnalysis  
# 3)关于热点事件的搜索趋势
对于1)得到的历史语料，可以使用百度指数，新浪微博指数进行采集  
这部分参考我的百度指数采集项目BaiduIndexSpyder：https://github.com/liuhuanyong/BaiduIndexSpyder  
微博指数采集项目WeiboIndexSpyder：https://github.com/liuhuanyong/WeiboIndexSpyder
# 4)关于热点事件的话题分析
对于1)得到的历史语料，可以使用LDA,Kmeans模型进行话题分析  
这部分参考我的话题分析项目Topicluster：https://github.com/liuhuanyong/TopicCluster
# 5)关于热点事件的代表性文本分析
对于1)得到的历史语料，可以使用跨篇章的textrank算法，对文本集的重要性进行计算和排序  
这部分参考我的文本重要性分析项目ImportantEventExtractor：https://github.com/liuhuanyong/ImportantEventExtractor
# 6)关于热点事件新闻文本的图谱化展示
对于得到每个历史新闻事件文本，可以使用关键词，实体识别等关系抽取方法对文本进行可视化展示  
这部分内容，参考我的文本内容可视化项目项目TextGrapher：https://github.com/liuhuanyong/TextGrapher

# 结束语
关于事件监测的方法有很多，也有很多问题需要去解决，以上提出的方法只是一个尝试，就算法本身还有许多需要改进的地方  

If any question about the project or me ,see https://liuhuanyong.github.io/
