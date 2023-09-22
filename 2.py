# 导入必要的库并下载所需的数据
import nltk
nltk.download('gutenberg')
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import gutenberg
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis

alice_text = gutenberg.raw('carroll-alice.txt')

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
tokenized_text = [word_tokenize(t) for t in sent_tokenize(alice_text)]
processed_text = [[ps.stem(w.lower()) for w in sentence if w.isalnum() and w.lower() not in stop_words] for sentence in tokenized_text]

dictionary = Dictionary(processed_text)
corpus = [dictionary.doc2bow(text) for text in processed_text]
lda_model = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)


topics = lda_model.print_topics(num_words=5)
for topic in topics:
    print(f'Topic {topic[0]}: Words: {topic[1]}')


lda_vis = gensimvis.prepare(lda_model, corpus, dictionary)
pyLDAvis.save_html(lda_vis, 'lda_visualization.html')
pyLDAvis.display(lda_vis)

