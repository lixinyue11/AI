import json


def read_json(file_path):
    jaon_read=json.load(open(file_path,encoding='utf-8'))
    print(jaon_read)
    reslut=[]
    for i in jaon_read:
        reslut.append(i)
    return reslut

res=read_json('semantic_chunk_metadata.json')
def write_json(datasets,file):
    with open(file, 'w', encoding='utf-8') as outfile:
        json.dump(datasets, outfile, ensure_ascii=False, indent=4)

b=write_json(res,'semantic_chunk_metadata.json')