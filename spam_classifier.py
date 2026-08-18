import pandas as pd
import string
import nltk

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# Download stopwords once
nltk.download("stopwords")

# ------------------ Load Dataset ------------------
df = pd.read_csv("spam.csv", encoding="latin-1")

# Keep only required columns
df = df[["v1", "v2"]]
df.columns = ["label", "message"]

# Remove duplicate messages
df.drop_duplicates(inplace=True)

# ------------------ Text Preprocessing ------------------
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

def preprocess(text):
    text = text.lower()

    text = "".join(ch for ch in text if ch not in string.punctuation)

    words = text.split()

    words = [word for word in words if word not in stop_words]

    words = [stemmer.stem(word) for word in words]

    return " ".join(words)

df["processed_message"] = df["message"].apply(preprocess)

# ------------------ TF-IDF ------------------
vectorizer = TfidfVectorizer(max_features=4000)

X = vectorizer.fit_transform(df["processed_message"])
y = df["label"]

# ------------------ Train/Test Split ------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ------------------ Train Naive Bayes ------------------
model = MultinomialNB()

model.fit(X_train, y_train)

# ------------------ Predictions ------------------
predictions = model.predict(X_test)

# ------------------ Evaluation ------------------
print("Accuracy:", round(accuracy_score(y_test, predictions) * 100, 2), "%\n")

print(classification_report(y_test, predictions))

# ------------------ Test Custom Message ------------------
while True:
    msg = input("\nEnter a message (or type 'exit'): ")

    if msg.lower() == "exit":
        break

    cleaned = preprocess(msg)
    vector = vectorizer.transform([cleaned])

    result = model.predict(vector)[0]

    if result == "spam":
        print("Spam")
    else:
        print("Ham")
