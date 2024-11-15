import re
from collections import Counter
import os
import numpy as np
import pandas as pd
import copy
import sys
import pickle 
from graph_builder import graph

lib_path = '../frameworks/laravel-10.x/'

size_image = 50
min_subclasses = 0
max_subclasses = None

if len(sys.argv) > 1:
    lib_path = sys.argv[1] + '/'
lib = re.findall('[^(\\\|/)]+', lib_path)[-1]
if lib == 'src':
    lib = re.findall('[^(\\\|/)]+', lib_path)[-2]

class Parser:
    def __init__(self, lib_path):
        self.lib_path = lib_path
        self.list_classes = []
        self.list_classes_for_graph = []
        self.list_classes_for_html = ['<!DOCTYPE html><html><head><meta charset="utf-8"><title></title>\
            <style>body{background-color: #13191e}div{color: #d2d2d2; font-family: Trebuchet MS; font-size: 15px}\
            a{color: #55e1e6; font-family: Trebuchet MS; font-size: 15px}span{color: #efefef}.red{color: #e0876a}\
            .orange{color: #f9ccac}</style></head><span><i>The numbers are amount of subclasses and size of file</i></span><br><br>']
        self.list_files_sizes = []
        self.dict_classes_sizes = dict()
        
    def open_and_reg(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            file_readed = None
            try:
                file_readed = file.read()
                classes = re.findall('^class\s.*|^interface.*|^abstract.*|^trait.*', file_readed, re.MULTILINE)
            except UnicodeDecodeError:
                classes = []
            
            for i in classes:
                i = i.replace('\\', '.')
                #class is taken for graph and counter at least 3 characters in name 
                list_1_or_more_classes = re.findall('\w{3,}\.*', i)
                list_1_or_more_classes_origin = list_1_or_more_classes.copy()
                for k in list_1_or_more_classes_origin:
                    if k in {'class', 'extends', 'interface', 'abstract', 'implements', 'trait'} \
                    or k[-1] == '.':
                        list_1_or_more_classes.remove(k)
                self.list_classes.extend(list_1_or_more_classes)
                if len(list_1_or_more_classes) > 0:
                    self.dict_classes_sizes[list_1_or_more_classes[0]] = os.path.getsize(path)
                if len(list_1_or_more_classes) > 1:
                    for j in list_1_or_more_classes[1:]:
                        if list_1_or_more_classes[0] != j:
                            self.list_classes_for_graph.append([list_1_or_more_classes[0], j])

            if len(classes) > 0:
                self.list_classes_for_html.append(f'<a href="{path}">{path}</a>&nbsp&nbsp&nbsp\
                <span style="color: rgb(50 ,50, blue)">{os.path.getsize(path)}</span>')
                self.list_files_sizes.append(os.path.getsize(path))
            
            for c in classes:
                c_html = copy.deepcopy(c)
                c_html = c_html.replace('{', '')
                c_html = c_html.replace('}', '')
                c_html = c_html.replace('<', '&lt')
                c_html = c_html.replace('>', '&gt')
                self.list_classes_for_html.append(f'<div>{c_html}</div>')
                # methods and fields for html
                list_file = file_readed.split('\n')
                for i in range(len(list_file)):
                    if list_file[i] == c:
                        try:
                            while list_file[i+1] == '' or list_file[i+1][0] in ('\t', '{', ' '):
                                if path[-2:] == 'va' or path[-2:] == 'ss':
                                    i += 1
                                    if re.findall('^(\t|\s)+(public|private|protected).*', list_file[i]):
                                        string = list_file[i]
                                        string = string.replace('<', '&lt')
                                        string = string.replace('>', '&gt')
                                        self.list_classes_for_html.append(f'<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{string}</div>')
                                else:
                                    i += 1
                                    list_file[i] = list_file[i].replace('\t', '    ')
                                    if re.findall('^\s{1,}def\s.*|^\s{1,}(public|private|protected|final|function|abstract).*|^\s{1,4}\w+\(.*', list_file[i]):
                                        self.list_classes_for_html.append(f'<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{list_file[i]}</div>')
                        except IndexError:
                            pass
            
    #run previous function on multiple files
    def print(self, tuple_from_oswalk):
        files = tuple_from_oswalk[2]
        for f in files:
            if tuple_from_oswalk[0][-1] != '/' and f[-2:] in {'hp', 'js', 'ts', 'py', 'va', 'ss'}:
                self.open_and_reg(tuple_from_oswalk[0] + '/' + f)
            elif tuple_from_oswalk[0][-1] == '/' and f[-2:] in {'hp', 'js', 'ts', 'py', 'va', 'ss'}:
                self.open_and_reg(tuple_from_oswalk[0] + f)
    
    #run in multiple directories
    def run(self):
        for i in os.walk(self.lib_path):
            self.print(i)
                

class Post_processing:
    def __init__(self, lib, list_classes, list_files_sizes, list_classes_for_html):
        self.lib = lib
        self.list_classes_for_html = list_classes_for_html
        self.list_files_sizes = list_files_sizes
        self.list_classes = list_classes
        self.class_counter_gt_1 = {}
        self.class_counter_lt_gt = set()
        self.dict_colors_for_sizes = None
        self.class_counter_gt_1_origin = None
    
    def count(self):
        class_counter = Counter(self.list_classes)

        for i in class_counter.items():
            if i[1] > 1:
                self.class_counter_gt_1[i[0]] = i[1]
            if max_subclasses == None:
                if i[1] < min_subclasses + 1:
                    self.class_counter_lt_gt.add(i[0])
            if max_subclasses != None:
                if max_subclasses + 1 < i[1] or i[1] < min_subclasses + 1:
                    self.class_counter_lt_gt.add(i[0])          
            
        self.class_counter_gt_1_origin = self.class_counter_gt_1.copy()

        #list of frequent classes in footer of html file
        self.list_classes_for_html.append('<br><span><b>Classes counter:</b></span><br>')
        for i in sorted(self.class_counter_gt_1_origin.items(), key= lambda item: item[1], reverse=True):
            self.list_classes_for_html.append(f'<a href="#{i[0]}">{i[0]}({i[1] - 1})</a>&nbsp&nbsp')

        #values of class_counter_gt_1 have been changed for convenient colors
        dict_line = dict(zip(sorted(set(self.class_counter_gt_1.values()), reverse=True), \
                             np.linspace(0, 255, len(set(self.class_counter_gt_1.values())))))

        for k, v in self.class_counter_gt_1.items():
            self.class_counter_gt_1[k] = dict_line[v]
    
        self.dict_colors_for_sizes = dict(zip(sorted(self.list_files_sizes),\
                                         np.linspace(0, 255, len(self.list_files_sizes))))

    #added colors and counter values in html
    def paint(self):
        for i in range(len(self.list_classes_for_html)):
            access_modifier = re.findall('private|protected|f\s__|f\s_', self.list_classes_for_html[i])
            if len(access_modifier) > 0:
                if access_modifier[0] == 'protected' or access_modifier[0] == 'f _':
                    self.list_classes_for_html[i] = re.sub('<div>', '<div class="orange">', self.list_classes_for_html[i])
                if access_modifier[0] == 'private' or access_modifier[0] == 'f __':
                    self.list_classes_for_html[i] = re.sub('<div>', '<div class="red">', self.list_classes_for_html[i])
                    
            size_for_color = re.findall('ue\)">\d*', self.list_classes_for_html[i])
            if len(size_for_color) > 0:
                self.list_classes_for_html[i] = re.sub('blue', \
                             str(self.dict_colors_for_sizes[int(size_for_color[0][5:])]), self.list_classes_for_html[i])
            try:
                c = re.findall('class\s\w+|interface\s\w+', self.list_classes_for_html[i])
            except:
                c = []
            if len(c) != 0:
                for j in self.class_counter_gt_1:
                    if j == c[0].split(' ')[1]:
                        self.list_classes_for_html[i] = '<div style="color: rgb(' + \
                        str(self.class_counter_gt_1[j]) + ' ,255 ,' + str(self.class_counter_gt_1[j]) + \
                        f')"  id="{j}">' + self.list_classes_for_html[i][5:-6] + \
                        f' = {self.class_counter_gt_1_origin[j] - 1}</div>'

    def save(self):
        self.count()
        self.paint()
        html_file = open(self.lib + '.html', 'w', encoding="utf-8")
        html_file.write('\n'.join(map(str, self.list_classes_for_html)))
        html_file.close()

if __name__ == '__main__':
    print("Parsing data")
    
    p = Parser(lib_path)
    p.run()

    pp = Post_processing(lib, p.list_classes, p.list_files_sizes, p.list_classes_for_html)
    pp.save()

    print("Plotting graph")
    #create graph
    graph(lib, p.list_classes_for_graph, p.dict_classes_sizes, pp.class_counter_lt_gt, size_image, min_subclasses, max_subclasses)
