from collections import Counter
import sys
import spacy
import wikipediaapi
import re

nlp = spacy.load("en_core_web_md")

def keyphrase_extractor(doc):
    """
    Attempt to extract the topic the user wants to learn about.
    If we are unable to extract the topic, ask the user to rephrase their input and try again
    until extraction is successful.

    :param doc: A spaCy Doc object created from a user input string.
    :return: Returns a string of representing the topic the user wants to learn about, if it is able to be determined.
             Returns False if we are unable to determine the topic.
    """

    noun_part_of_speech_list = ["NOUN", "PROPN"]
    

    for token in doc:
        # We are specifically looking for nouns or proper nouns.
        if not token.pos_ in noun_part_of_speech_list:
            continue

        # If we find a noun that serves as the object of preposition in a sentence,
        # return a string that combines all of its left children + itself.
        # An example of a sentence that would apply to this logic is "Can you tell me about wild animals?"
        # The returned string would be "wild animals".
        if token.dep_ == 'pobj':
            return (' '.join([child.text for child in token.lefts]) + ' ' + token.text).lstrip()


    # Look through doc in reverse because we only return the first direct object we find, and the 
    # direct object we care about is likely at the end of the sentence.
    for token in reversed(doc):
        # We are specifically looking for nouns or proper nouns.
        if not token.pos_ in noun_part_of_speech_list:
            continue

        # If we find a direct object, return a string that combines its children that modify it + itself.
        # An example sentence that would apply to this logic is "I want to eat italian food".
        # The returned sentence would be "italian food".
        if token.dep_ == 'dobj':
            children = [child.text for child in token.children if child.dep_ in ["compound", "amod"]]
            return ' '.join(children) +  ' ' + token.text

            
    return False

def get_wiki_article(phrase):
    """
    Uses the wikipediaapi library to retrieve and return the wikipedia page dedicated to the argument passed in.

    :param phrase: A string representing the topic the user wanted to know about.
    :returns: A wikipediaapi.WikipediaPage object.
    """
    return wikipediaapi.Wikipedia('en').page(phrase)

def print_wiki_summary(wiki_page):
    """
    Prints the title, a summary, and the URL for the Wikipedia page passed in as an argument.

    :param wiki_page: A wikipediaapi.WikipediaPage object.
    """
    print("Page Title: % s" % wiki_page.title.title())
    print("Page Summary: % s" % wiki_page.summary[0:100])
    print("Page URL: % s" % wiki_page.fullurl)

def location_extractor(wiki_page):
    """
    Parse the spaCy Doc object passed as an argument for any locations.
    Return a list of these locations.

    :param doc: A spaCy Doc object created from a user input string.
    :returns: A list of strings representing geo-political entities.
    """
    locations = []
    for ent in wiki_page.ents:
        for word in ent:
            if word.ent_type_ == "GPE":
                locations.append(ent.text.title())
    return locations

def sort_locations_by_frequency(location_list):
    """
    Calculate the frequency of the values in the list passed as an argument and a return a unique list containing the values in descending order of
    how frequently they were found.

    :param location_list: A list of strings representing geo-political locations.
    :returns: A list containing unique values in descending order of frequently they were found in the list passed to this function.
    """
    location_count_dict = Counter(location_list)
    return [location[0] for location in sorted(location_count_dict.items(), key = lambda item: item[1], reverse = True)]

def find_similar_words(wiki_page, keyphrase):
    """
    Given a wikipediaapi.WikipediaPage object and a spaCy Doc object, return a unique list of words from the Wikipedia pages text that are similar
    to the spaCy Doc object. Specifically, we return words that have a > 0.80 similarity to our spaCy Doc object.

    :param wiki_page: A wikipediaapi.WikipediaPage object.
    :param keyphrase: A spaCy Doc object.
    :returns: A unique list of strings representing words that are similar to the keyphrase argument.
    """
    similar_words = []
    text_array = wiki_page.text.split(" ")
    text_array = list(set(text_array))
    for word in text_array:
        processed_word = nlp(re.sub(r"[^a-zA-Z0-9 ]", "", word))
        if processed_word.text.lower() != keyphrase.text.lower() and keyphrase.similarity(processed_word) > 0.80:
            similar_words.append(processed_word.text.title().strip())
    return list(set(similar_words))


# Get original input from user and process it with spaCy.
statement = nlp(str(input("Give me a statement about what you would like to learn about: ")))

# Set default values for variables to allow us to loop until we can properly set them below.
keyphrase = False
wiki_page = False

# Loop to allow retrying until we can successfully extract the topic of the user's sentence.
while not keyphrase:
    keyphrase = keyphrase_extractor(statement)
    if not keyphrase:
        statement = nlp(str(input("We were unable to determine the topic you want to know about. Please rephrase your statement and try again: ")))

# Loop to allow retrying until we can successfully find a Wikipedia page for the topic the user is interested in.
while not wiki_page:
    wiki_page = get_wiki_article(keyphrase)
    if not wiki_page.exists():
        statement = nlp(str(input("We were unable to find a Wikipedia page for your topic. Please try again with another topic: ")))
        keyphrase = keyphrase_extractor(statement)
        wiki_page = False

print_wiki_summary(wiki_page)

doc = nlp(wiki_page.text)
locations = location_extractor(doc)

print("Here are the 10 most frequently associated places with your topic: \n")
for location in sort_locations_by_frequency(locations)[0:10]:
    print("%s \n" % location)

print("Here are words that are similar to your topic: \n")
for word in find_similar_words(wiki_page, nlp(keyphrase)):
    print("%s \n" % word)