# NLP-Learning-Assistant
Small program which utilizes the spaCy library to interpret the topic the user wants to learn about, and then fetches / parses the Wikipedia page on that topic for the user.

This is a short personal project that served as an introduction to Natural Language Processing (NLP) after spending a weekend learning about it. The script asks the user what they would like to learn about and attempts to process the user input to determine their intent (asking them to rephrase if unable to determine their intent). Once successfully determining the user's intent, the script will retrieve the Wikipedia article related to the user's topic and provide an overview of information from it. 
This overview includes:
- The article title
- A summary of the article
- The URL of the article
- The 10 Geo-Political Entities most often referenced in the article.
- A list of words that are similar to the topic the user wanted to learn about.


## Places for Improvement

1. The `keyphrase_extractor` function could be improved to be better at recognizing and extracting user intent. Currently it is only capable of determining intent when the sentence contains an object of preposition, or a direct object. Sentences that express intent using a nominal subject, such as "Do you know how flowers grow?", would not be understood and the user would be asked to rephrase their input. More complicated inputs that use multiple object of preposition or direct objects would also likely give unexpected results.
2. The `find_similar_words` function could be improved to be more efficient in determining similar words, and likely more efficient with space and time as well. One way to potentially improve the ability to find similar words would be to use spaCy to compare the similarity of the lemma of two words, as opposed to the words themselves. There are also likely ways to improve space / time efficiency by parsing down the list of words to check against the user's topic further so that we run the NLP pipeline fewer times.
