#Test save file
import json
from sklearn.metrics import confusion_matrix

chan_dict_vals = {1:[1,2,3],3:[1,2]}
psth_templates = {1:[1,2,3],3:[1,2]}
data_nums = [9,12,14,9,12,14,9,12,14]
data2 = {'confmat':data_nums}
data_nums_2 = [9,9,9,9,9,9,9,9,9]
data3 = {'stuff':data_nums_2}
data2.update(data3)
chan_dict = {'chandict':chan_dict_vals}
data2.update(chan_dict)

print('actual events:y axis, predicted events:x axis')

print(confusion_matrix(data_nums,data_nums_2))

jsondata = psth_templates
print(jsondata)
jsondata.update(data2)
print(jsondata)

name = input('What would you like to name the template file:')
# with open(name +'.txt', 'w') as outfile:
#     json.dump(jsondata, outfile)


print('load')

with open(name + '.txt') as infile:
    data = json.load(infile)



loaded_data = {}
loaded_data_word = {}
print(data)
for i in data.keys():
    if i.isnumeric():
        print('key')
        print(i)
        temp_dict = {i:data[i]}
        print(temp_dict)
        loaded_data.update(temp_dict)
    else:
        if i == 'confmat':
            print('confmat')
        if i == 'stuff':
            print('stuff')
        if i == 'ChannelDict':
            print('chandict')
            loaded_chan_map = {i:data[i]}
        print('word key')
        temp_dict_word = {i:data[i]}
        print(temp_dict_word)
        loaded_data_word.update(temp_dict_word)
for i in loaded_chan_map.keys():
    new_chan_map = data[i]
    print('new_chan_map',new_chan_map)
##print(loaded_data)
##print(loaded_data_word)
