from TranslationAPI import translationAPI
from StructureFilter import StanfordParser
import re
import consistency_analysis
import jieba

similarity_threshold = 0.9


def generate_sentence(ori_source_sentence, sim_dict):
    """
    生成变异语句, 经结构筛选后返回
    :param ori_source_sentence: 原句(已经去除标点符号)
    :param sim_dict: 上下文相似语料库(已经经过词性判断，均为名词、形容词、数字)
    :param number: 生成变异句的数量
    :return:变异语句
    """
    # line = re.sub(r"[^A-Za-z\s]", "", ori_source_sentence.strip())
    print("\033[1;31m 变异句：\033[0m")
    line = ori_source_sentence
    word_arr = line.split(" ")
    new_source_sentences = []
    # 替换单词
    for i in range(0, len(word_arr)):
        word = word_arr[i].lower()

        if word not in sim_dict.keys():
            continue
        for replace_word in sim_dict[word]:
            word_arr[i] = replace_word
            new_source_sentence = " ".join(word_arr).capitalize()
            print(new_source_sentence)
            # 结构过滤
            if StanfordParser.structureFilter(line, new_source_sentence):
                new_source_sentences.append(new_source_sentence)
        word_arr[i] = word

    return new_source_sentences


def repair_translation(ori_source_sentence, sim_dict):
    """

    :param ori_source_sentence: 英文原句
    :return: 原翻译，修复翻译
    """
    # 去除标点符号
    ori_source_sentence = re.sub(r"[^A-Za-z\s']", "", ori_source_sentence)
    # 翻译原句
    # ori_target_sentences: [{'src':'...', 'dst':'...'},...]
    ori_target_sentence = ""

    ori_target_sentence = translationAPI.translationBlackBox(ori_source_sentence)[0]['dst']

    print("\033[1;31m 原句翻译：\033[0m", ori_target_sentence)
    # 变异原句
    new_source_sentences = generate_sentence(ori_source_sentence, sim_dict)
    # 翻译变异语句
    print("\033[1;31m 过滤后变异句：\033[0m")
    new_target_sentences = []
    for new_source_sentence in new_source_sentences:
        new_target_sentence = translationAPI.translationBlackBox(new_source_sentence)[0]['dst']
        new_target_sentences.append(new_target_sentence)
        print(new_source_sentence)
        print(new_target_sentence)

    # 翻译一致性分析
    print("\033[1;31m 翻译一致性分析: \033[0m")
    suspicious_target_sentences = []  # 有一致性问题的变异句翻译
    suspicious_source_sentences = []
    for i in range(0, len(new_target_sentences)):
        t = new_target_sentences[i]
        s = new_source_sentences[i]
        score = consistency_analysis.consistency_score(t, ori_target_sentence)
        print(t, "相似分数：", score)
        if score < similarity_threshold:
            suspicious_source_sentences.append(s)
            suspicious_target_sentences.append(t)
    if len(suspicious_source_sentences) == 0:
        print("\033[1;31m 没有翻译不一致问题 \033[0m")
        return ori_target_sentence, ori_target_sentence
    print("\033[1;31m 存在翻译不一致问题的变异句：\033[0m")
    print(suspicious_source_sentences)
    print(suspicious_target_sentences)

    # 修复不一致性翻译
    T = list()
    T.append({'src': ori_source_sentence, 'target': ori_target_sentence, "score": 0})
    for i in range(0, len(suspicious_source_sentences)):
        T.append({"src": suspicious_source_sentences[i], "target": suspicious_target_sentences[i], "score": 0})

    # 排序

    for i in range(0, len(T)):
        score = 0
        for j in range(0, len(T)):
            score += consistency_analysis.computeSimilarity(T[i]["target"], T[j]["target"])
        T[i]["score"] = score / len(T)

    T = sorted(T, key=lambda x: x['score'], reverse=True)
    print("\033[1;31m 排序完成：\033[0m")
    for t in T:
        print(t)

    # 修复
    print("\033[1;31m 开始修复 \033[0m")

    for t in T:
        if t['src'] == ori_source_sentence:
            print("原句排序最高，无需修复")
            return ori_target_sentence, ori_target_sentence
        ori_src_cut = ori_source_sentence.split(" ")
        t_src_cut = t['src'].split(" ")
        ori_diff_word = ""
        new_diff_word = ""
        for i in range(0, len(t_src_cut)):
            if ori_src_cut[i] != t_src_cut[i]:
                ori_diff_word = ori_src_cut[i]
                new_diff_word = t_src_cut[i]
                break
        trans_ori_diff_word = translationAPI.translationBlackBox(ori_diff_word)[0]['dst']
        trans_new_diff_word = translationAPI.translationBlackBox(new_diff_word)[0]['dst']
        t_target_cut = list(jieba.cut(t['target']))
        flag = False
        for i in range(0, len(t_target_cut)):
            if trans_new_diff_word == t_target_cut[i]:
                flag = True
                t_target_cut[i] = trans_ori_diff_word
                break
        if flag:
            repair_trans = "".join(t_target_cut)
        else:
            repair_trans = ori_target_sentence

        return ori_target_sentence, repair_trans

    return ori_target_sentence, ori_target_sentence


def repair_file(ori_file, target_file_path, repair_file_path, RQ1, RQ2, RQ3, sim_dict):
    """
    以文件为单位进行翻译修复
    :param ori_file: 原文件(英文,需要预处理,英文每一句需要换行)
    :param repair_file_path: 修复后的翻译文件地址
    :param RQ1: RQ1~3为实验验证输出文件，具体见文档，可删除
    :param RQ2:
    :param RQ3:
    :param sim_dict: 上下文相似语料库
    """
    with open(repair_file_path, 'w', encoding='utf-8') as f:
        f.write("")
    with open(target_file_path, 'w', encoding='utf-8') as f:
        f.write("")
    with open(RQ1, 'w', encoding='utf-8') as f:
        f.write("")
    with open(RQ2, 'w', encoding='utf-8') as f:
        f.write("")
    with open(RQ3, 'w', encoding='utf-8') as f:
        f.write("")

    with open(ori_file, 'r') as f:
        lines = f.readlines()
        for ori_source_sentence in lines:
            ori_source_sentence = ori_source_sentence.capitalize().replace('\n', '')
            if ori_source_sentence == "":
                continue
            new_source_sentences = generate_sentence(ori_source_sentence, sim_dict)
            # 写入RQ1
            with open(RQ1, 'a', encoding='utf-8') as RQ1_file:
                RQ1_file.write("原句：")
                RQ1_file.write(ori_source_sentence + '\n')
                RQ1_file.write("变异句：\n")
                for new_source_sentence in new_source_sentences:
                    RQ1_file.writelines(new_source_sentence + '\n')
            ori_translation, repair_sentence = repair_translation(ori_source_sentence, sim_dict)
            repair_sentence += '\n'
            ori_translation += '\n'
            if repair_sentence != ori_translation:
                with open(RQ2, 'a', encoding='utf-8') as RQ2_file:
                    RQ2_file.write('原句：' + ori_source_sentence)
                    RQ2_file.write('原句翻译：' + ori_translation)
                with open(RQ3, 'a', encoding='utf-8') as RQ3_file:
                    RQ3_file.write('原句：' + ori_source_sentence)
                    RQ3_file.write('原句翻译：' + ori_translation)
                    RQ3_file.write('修复：' + repair_sentence)
                    RQ3_file.write('Label: \n')
            with open(target_file_path, 'a', encoding='utf-8') as target_file:
                target_file.writelines(ori_translation)
            # 写入修复文件
            with open(repair_file_path, 'a', encoding='utf-8') as repair_file:
                repair_file.writelines(repair_sentence)


if __name__ == "__main__":
    # 初始化
    data_set = 'test.txt'

    # 加载上下文相似语料库
    sim_dict_file = "SimilarCorpus/similarity_dict.txt"
    sim_dict = {}
    with open(sim_dict_file, 'r') as f:
        lines = f.readlines()
        for l in lines:
            sim_dict[l.split()[0]] = l.split()[1:]
    print("\033[1;31m 加载上下文相似语料库 \033[0m")
    repair_file("dataset/test.txt", "dataset/test_target.txt", "dataset/test_repair.txt", "dataset/RQ1.txt", "dataset/RQ2.txt", "dataset/RQ3.txt", sim_dict)
    # while True:
    #     # 输入原语句,一次输入一句,不包括回车
    #     ori_source_sentence = input("输入语句: ").capitalize()
    #     if ori_source_sentence == "END":
    #         break
    #     ori_translation, repair = repair_translation(ori_source_sentence, sim_dict)
    #     print("\033[1;31m 修复翻译: \033[0m", repair)

    StanfordParser.stanford_nlp_close()
