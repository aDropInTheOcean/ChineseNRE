#coding:utf-8
import numpy as np
import pickle
import sys
import codecs

import torch
import torch.nn as nn
import torch.optim as optim

import torch.utils.data as D
from torch.autograd import Variable
from BiLSTM_ATT import BiLSTM_ATT

#with open('./data/engdata_train.pkl', 'rb') as inp:
with open('./data/people_relation_train.pkl', 'rb') as inp:
    word2id = pickle.load(inp)
    id2word = pickle.load(inp)
    relation2id = pickle.load(inp)
    train = pickle.load(inp)
    labels = pickle.load(inp)
    position1 = pickle.load(inp)
    position2 = pickle.load(inp)

#with open('./data/engdata_test.pkl', 'rb') as inp: 
with open('./data/people_relation_test.pkl', 'rb') as inp:
    test = pickle.load(inp)
    labels_t = pickle.load(inp)
    position1_t = pickle.load(inp)
    position2_t = pickle.load(inp)


print("train len", len(train) )
print("test len", len(test))
print("word2id len",len(word2id))

device = torch.device("cuda")

EMBEDDING_SIZE = len(word2id)+1        
EMBEDDING_DIM = 100

POS_SIZE = 82  #不同数据集这里可能会报错。
POS_DIM = 25

HIDDEN_DIM = 200

TAG_SIZE = len(relation2id)

BATCH = 128
EPOCHS = 100

config={}
config['EMBEDDING_SIZE'] = EMBEDDING_SIZE
config['EMBEDDING_DIM'] = EMBEDDING_DIM
config['POS_SIZE'] = POS_SIZE
config['POS_DIM'] = POS_DIM
config['HIDDEN_DIM'] = HIDDEN_DIM
config['TAG_SIZE'] = TAG_SIZE
config['BATCH'] = BATCH
config["pretrained"]=False

learning_rate = 0.0005


embedding_pre = []
if len(sys.argv)==2 and sys.argv[1]=="pretrained":
    print("use pretrained embedding")
    config["pretrained"]=True
    word2vec = {}
    with codecs.open('vec.txt','r','utf-8') as input_data:   
        for line in input_data.readlines():
            word2vec[line.split()[0]] = map(eval,line.split()[1:])

    unknow_pre = []
    unknow_pre.extend([1]*100)
    embedding_pre.append(unknow_pre) #wordvec id 0
    for word in word2id:
        if word2vec.has_key(word):
            embedding_pre.append(word2vec[word])
        else:
            embedding_pre.append(unknow_pre)

    embedding_pre = np.asarray(embedding_pre)
    print(embedding_pre.shape)

model = BiLSTM_ATT(config,embedding_pre)
#model = torch.load('model/model_epoch20.pkl')
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
criterion = nn.CrossEntropyLoss(size_average=True)



train = torch.LongTensor(train[:len(train)-len(train)%BATCH])
position1 = torch.LongTensor(position1[:len(train)-len(train)%BATCH])
position2 = torch.LongTensor(position2[:len(train)-len(train)%BATCH])
labels = torch.LongTensor(labels[:len(train)-len(train)%BATCH])
train_datasets = D.TensorDataset(train,position1,position2,labels)
train_dataloader = D.DataLoader(train_datasets,BATCH,True,num_workers=2)


test = torch.LongTensor(test[:len(test)-len(test)%BATCH])
position1_t = torch.LongTensor(position1_t[:len(test)-len(test)%BATCH])
position2_t = torch.LongTensor(position2_t[:len(test)-len(test)%BATCH])
labels_t = torch.LongTensor(labels_t[:len(test)-len(test)%BATCH])
test_datasets = D.TensorDataset(test,position1_t,position2_t,labels_t)
test_dataloader = D.DataLoader(test_datasets,BATCH,True,num_workers=2)
#test_dataloader = D.DataLoader(test_datasets,BATCH,True)

if __name__ == '__main__':
    dic_f = {}  # zw
    best_f1score = 0  # zw
    for i in range(70, 220, 30):  # zw
        EPOCHS = i  # zw
        f1score = 0
        for epoch in range(EPOCHS):
            print("epoch:", epoch)
            acc = 0
            total = 0

            for sentence, pos1, pos2, tag in train_dataloader:
                sentence = Variable(sentence)
                pos1 = Variable(pos1)
                pos2 = Variable(pos2)
                y = model(sentence, pos1, pos2)
                tags = Variable(tag)
                loss = criterion(y, tags)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                y = np.argmax(y.data.numpy(), axis=1)

                for y1, y2 in zip(y, tag):
                    if y1 == y2:
                        acc += 1
                    total += 1

            print("train:", 100 * float(acc) / total, "%")

            acc_t = 0
            total_t = 0
            count_predict = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            count_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            count_right = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for sentence, pos1, pos2, tag in test_dataloader:
                sentence = Variable(sentence)
                pos1 = Variable(pos1)
                pos2 = Variable(pos2)
                y = model(sentence, pos1, pos2)
                y = np.argmax(y.data.numpy(), axis=1)
                for y1, y2 in zip(y, tag):
                    count_predict[y1] += 1
                    count_total[y2] += 1
                    if y1 == y2:
                        count_right[y1] += 1

            precision = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            recall = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(len(count_predict)):
                if count_predict[i] != 0:
                    precision[i] = float(count_right[i]) / count_predict[i]

                if count_total[i] != 0:
                    recall[i] = float(count_right[i]) / count_total[i]

            precision = sum(precision) / len(relation2id)
            recall = sum(recall) / len(relation2id)
            f1score = (2 * precision * recall) / (precision + recall)  # zw
            print("准确率：", precision)
            print("召回率：", recall)
            print("f：", f1score)  # zw

            if epoch % 20 == 0:
                model_name = "./model/model_epoch" + str(epoch) + ".pkl"
                torch.save(model, model_name)
                print(model_name, "has been saved")
        dic_f[EPOCHS] = f1score  # zw
        if f1score>best_f1score:  # zw
            best_f1score = f1score  # zw
            torch.save(model, "./model/model_01.pkl")  # zw
            print("new best model has been saved")  # zw
    print(dic_f)




