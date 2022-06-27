import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, plot_confusion_matrix
import joblib
import os

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
# add more later + deep learning

# load data
note_data = pd.read_excel(r'~/notes-ml-app/data_final.xlsx', names = ['Note', 'Category'])

# shuffle data
note_data = note_data.sample(frac=1, random_state=42).reset_index(drop=True)

# see unique category or categories
print(note_data.groupby(['Category']).size().reset_index().drop(columns=0))

# split into train and test data
Xfeature = note_data['Note']
ylabels = note_data['Category']
X_train, X_test, y_train, y_test = train_test_split(Xfeature, ylabels, test_size = 0.3, random_state = 7)

pipe_lst = []

# Naive Bayes 
pipe_nb = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                      ('clf', MultinomialNB()),])
pipe_nb.fit(X_train, y_train)
pipe_lst.append(pipe_nb)
print('NB', pipe_nb.score(X_test, y_test))

# SVM
pipe_svm = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                      ('clf-svm', SGDClassifier(loss='modified_huber', penalty='l2', alpha=1e-3, n_iter_no_change=5, random_state=42)),])
pipe_svm.fit(X_train, y_train)
pipe_lst.append(pipe_svm)
print('SVM', pipe_svm.score(X_test, y_test))

# GridSearch NB
parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
            'tfidf__use_idf': (True, False),
             'clf__alpha': (1e-2, 1e-3),}

gs_clf = GridSearchCV(pipe_nb, parameters, n_jobs=-1)
gs_clf = gs_clf.fit(X_train, y_train)
pipe_lst.append(gs_clf)
print('GridSearch NB', gs_clf.score(X_test, y_test))

# GridSearch SVM
parameters_svm = {'vect__ngram_range': [(1, 1), (1, 2)],
             'tfidf__use_idf': (True, False),
            'clf-svm__alpha': (1e-2, 1e-3),}

gs_clf_svm = GridSearchCV(pipe_svm, parameters_svm, n_jobs=-1)
gs_clf_svm = gs_clf_svm.fit(X_train, y_train)
# gs_clf_svm.best_score_
# gs_clf_svm.best_params_

pipe_lst.append(gs_clf_svm)
print('GridSearch SVM', gs_clf_svm.score(X_test, y_test))

# dump best model
max_score = 0
best_model = None
for p in pipe_lst:
   current_score = p.score(X_test, y_test)
   if current_score > max_score:
      max_score = current_score
      best_model = p
print('Dumped', best_model, "Score:", best_model.score(X_test, y_test))

print(X_train, y_train)

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, r'/Users/arifeensaeed/notes-ml-app/clf_final.pkl') # replace with your own username and file location
joblib.dump(best_model, filename )

print(best_model.classes_)

# joblib.dump(best_model, "clf_final.pkl")