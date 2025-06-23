import torch


def get_vec(self, sentences):
    # 否则使用原始BERT方法
    encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = self.model(**encoded_input)
    sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
    sentence_embeddings = sentence_embeddings.data.cpu().numpy().tolist()
    return sentence_embeddings
