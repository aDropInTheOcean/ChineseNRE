# ChineseNRE

本项目使用
将原版改成了适合于
+ python 3.6
+ pytorch 1.0.0

的版本

中文实体关系抽取，对实体关系抽取不了解的可以先看<a href="https://blog.csdn.net/buppt/article/details/82961979">这篇文章</a>。顺便求star～

## 数据
中文实体关系抽取数据实在太难找了，data中是忘记在哪里找的人物关系数据集，一共11+1种关系，数据质量不太好，但也找不到其他的了。 （更新）<a href="https://github.com/buppt/ChineseNRE/issues/7">issues7</a>中 ybNero 同学分享了一份数据集，大家可以去issues中查看~
```
梅葆玥	梅兰芳	父母 坎坷经历梅葆玥之家庭合影1961年，梅兰芳先生病逝，葆玥、葆玖姐弟俩继承父亲的遗志，挑起了梅剧团的重担
```

数据格式为: 实体1 实体2 关系 句子。

虽然叫中文实体关系抽取，还是增加了一个英文数据集SemEval2010_task8，简单做了下数据处理，这是免费的公开数据集，其他的好像都要dollar了。。

## 训练
模型使用的是lstm+attention模型。特征使用词向量+位置向量。

训练前先运行data文件夹中的 `data_util.py` 文件，将数据处理成pkl文件供模型使用。

运行`python train.py`即可开始训练，可以在`train.py`文件中设置epoch、batch等参数，运行结束模型会储存到model文件夹中，可以在训练好的模型基础上继续训练。

可以运行`python train.py pretrained`使用预训练的词向量进行训练。vec.txt是一个训练好的词向量的例子，可以修改使用更加优秀的预训练词向量。

## 准确率
奈何实验室没有服务器，只能用自己电脑的cpu跑了一小部分数据，结果如下。

| 准确率 | 召回率 | F1值 |
| ------ | ------ | ------ |
| 64.08% | 64.59% | 64.33% |



## 参考
Attention-Based Bidirectional Long Short-Term Memory Networks for Relation Classification

## 更新日志
2018-10-7 第一版，不定期进行修改与优化。

2018-10-9 添加准确率、召回率、f值的计算，将model从`train.py`中分离。

2018-10-10 添加SemEval2010_task8数据，以及一些小修改。

2018-10-18 增加预训练的词向量，修改bug。

