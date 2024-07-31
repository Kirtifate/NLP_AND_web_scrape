#!/usr/bin/env python
# coding: utf-8

# The assignment involves extracting textual data from articles at the provided URL and performing text analysis to compute variables as described in the objective/text analysis file.

# 1.WEB SCRAPING 
# 
# Here I have created a function which hit each URL from the input file and extract the title and content of that file.
# I have used goose library as it is easier to extract by the names such as article.title and article.text.
# 
# This same process can be done using other various methods like searching for paragraphs (p) in the HTML code and many other techniques.
# 
# After extracting the content ,file is saved by the URL_ID which is consist in the row 0.Also,I have given condition that if there is no URL in the row,then it should skip that row.(This is helpful for reducing the time consumed by the program)

# In[1]:


import pandas as pd
from goose3 import Goose
import requests

# Read the CSV file
df = pd.read_csv('C:/Users/Kirti/Desktop/web_scrape and analysis/Input.csv')

# Initialize Goose
goose = Goose()

def extract_and_save_content(file_name, url):
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()
        # Extract cleaned text using Goose
        article = goose.extract(raw_html=response.content)
        title = article.title
        cleaned_text = article.cleaned_text

        # Save the cleaned text to a file
        with open(file_name, 'w', encoding='utf-8') as text_file:
            text_file.write(title + '\n\n')
            text_file.write(cleaned_text)
        
        print(f"Successfully saved content from {url} to {file_name}")
    
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Iterate through each row in the dataframe
for index, row in df.iterrows():
    file_name = f"C:/Users/Kirti/Desktop/Output_folder/Scraped data/{row[0]}"
    url = row[1]  # Assuming the first column is the file name and the second column is the URL
    
    # Check if the URL is not null or empty
    if pd.isna(url) or url.strip() == "":
        print(f"No URL provided for row {index}. Skipping...")
        continue
    
    extract_and_save_content(file_name, url)


# 2.TEXT ANALYSIS 
# 
# Text analysis is performed on the scraped data which I had extracted above.

# ## 1  IMPORTING THE LIBRARIES REQUIRED

# In[11]:


import os
import pandas as pd
from nltk.tokenize import word_tokenize, sent_tokenize
from textblob import TextBlob

#2.SO THERE IS A FOLDER WHICH HAS STOPWORDS IN IT.HERE I AM READING THAT FILE OF STOPWORDS.
# In[12]:


def read_stopwords(stopwords_folder):
    stopwords = set()
    for filename in os.listdir(stopwords_folder):
        file_path = os.path.join(stopwords_folder, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                words = file.read().split()
                stopwords.update(words)
    return stopwords


# In[13]:


def read_words_from_file(file_path):
    words = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        words.update(content.split())
    return words


# In[ ]:


#THIS IS A SEPRATE FUNCTION I HAD CREATED FOR CALCULATING THE SYLLABLE IN THE WORD.


# In[14]:


def syllable_count(word):
    vowels = "aeiou"
    word = word.lower()
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

# Here is the function 'calculate_scores' which is going to calculate all the values from positive score, negative score, polarity score, subjective score, average sentence length, percentage of complex words, fog index, average number of words, complex word count, word count, syllable per word, reasonable pronouns, average word length. this function takes the values of filtered content (content from the scraped data which is cleaned by removing stopwords), filtered positive words (there is the positive words file which you have provided (filtered positive words are those positive words which are not in stopwords (as instructed in the text analysis file)), same as filtered negative words. there are empty list I have created in a function 'read files from directory' so the calculated values from this function are going to append in that list. 
# In[15]:


def calculate_scores(filtered_content, filtered_positive_words, filtered_negative_words, pos_score, neg_score, polarity_scores, subjectivity_scores, average_Sentence_length, percentage_of_Complex_words, fog_index, average_number_of_words_per_Sen, complex_word_Count, word_Count, syllable_per_word, reasonable_pronouns, average_Word_length):
    positive_score = 0
    negative_score = 0
    
    words = filtered_content.split()
    sentences = sent_tokenize(filtered_content)
    blob = TextBlob(filtered_content)
    sentiment = blob.sentiment
    
    # Append sentiment scores to the lists
    polarity_scores.append(sentiment.polarity)     #this can be also calculated by the formula which utilized the positive and negative score.
    subjectivity_scores.append(sentiment.subjectivity)
    
    num_sentences = len(sentences)
    num_words = len(words)
    avg_sentence_length = num_words / num_sentences 
    average_Sentence_length.append(avg_sentence_length)
    #print(average_Sentence_length)
    num_complex_words = 0
    total_syllables = 0
    for word in words:
        syllable_count_per_word = syllable_count(word)
        total_syllables += syllable_count_per_word
        if syllable_count_per_word > 2:
            num_complex_words += 1
        if word in filtered_positive_words:
            positive_score += 1
        elif word in filtered_negative_words:
            negative_score += 1
    
    pos_score.append(positive_score)
    neg_score.append(negative_score)
    
    word_count = len(words)
    word_Count.append(word_count)
    
    percentage_complex = (num_complex_words / word_count) * 100 
    percentage_of_Complex_words.append(percentage_complex)
    
    fog_index_value = 0.4 * (avg_sentence_length + percentage_complex)
    fog_index.append(fog_index_value)
    
    average_number_of_words_per_Sen.append(avg_sentence_length)
    
    complex_word_Count.append(num_complex_words)
    
    avg_syllable_per_word = total_syllables / word_count 
    syllable_per_word.append(avg_syllable_per_word)
    
    pronouns = sum(1 for word in words if word.lower() in ["i", "we", "my", "ours", "us"])
    reasonable_pronouns.append(pronouns)
    
    total_word_length = sum(len(word) for word in words)
    avg_word_length = total_word_length / word_count
    average_Word_length.append(avg_word_length)

#This function will execute first. It will create filtered_content, filtered_positive_words, and filtered_negative_words. From this function, the calculate_score function will be called, which will calculate the scores for each text analysis. All the scores will then be appended to the specified output file as I detailed here.
# In[16]:


def read_files_in_directory(directory_path, stopwords_folder, excel_file_path):
    stop_words = read_stopwords(stopwords_folder)

    pos_score = []
    neg_score = []
    polarity_scores = []
    subjectivity_scores = []
    average_Sentence_length = []
    percentage_of_Complex_words = []
    fog_index = []
    average_number_of_words_per_Sen = []
    complex_word_Count = []
    word_Count = []
    syllable_per_word = []
    reasonable_pronouns = []
    average_Word_length = []
    
    # Read the existing Excel file
    df = pd.read_excel(excel_file_path,engine='openpyxl')

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):  # Ensure it's a file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                words = word_tokenize(content)
                sentences = sent_tokenize(content)
                
                filtered_words = [word for word in words if word.lower() not in stop_words]
                
                filtered_content = ' '.join(filtered_words)
                
                positive_words_file = 'C:/Users/Kirti/Desktop/web_scrape and analysis/MasterDictionary-20240619T074602Z-001/MasterDictionary/positive-words.txt'
                negative_words_file = 'C:/Users/Kirti/Desktop/web_scrape and analysis/MasterDictionary-20240619T074602Z-001/MasterDictionary/negative-words.txt'
                
                stopwords = read_stopwords(stopwords_folder)
                positive_words = read_words_from_file(positive_words_file)
                negative_words = read_words_from_file(negative_words_file)
                
                filtered_positive_words = [word for word in positive_words if word not in stopwords]
                filtered_negative_words = [word for word in negative_words if word not in stopwords]
                
                calculate_scores(filtered_content, filtered_positive_words, filtered_negative_words, pos_score, neg_score, polarity_scores, subjectivity_scores, average_Sentence_length, percentage_of_Complex_words, fog_index, average_number_of_words_per_Sen, complex_word_Count, word_Count, syllable_per_word, reasonable_pronouns, average_Word_length)

    # Truncate the DataFrame to the number of files processed
    num_files = len(polarity_scores)
    df = df.head(num_files)

    # Assign the sentiment scores to the corresponding columns(ASSIGNING VALUES TO THE ALREADY PRESENTED COLUMNS IN THE OUTPUT FILE)
    df['POLARITY SCORE'] = polarity_scores
    df['SUBJECTIVITY SCORE'] = subjectivity_scores  
    df['POSITIVE SCORE'] = pos_score  
    df['NEGATIVE SCORE'] = neg_score  
    df['AVG SENTENCE LENGTH'] = average_Sentence_length  
    
    # Assign the additional calculated scores
    df['PERCENTAGE OF COMPLEX WORDS'] = percentage_of_Complex_words
    df['FOG INDEX'] = fog_index
    df['AVG NUMBER OF WORDS PER SENTENCE'] = average_number_of_words_per_Sen
    df['COMPLEX WORD COUNT'] = complex_word_Count
    df['WORD COUNT'] = word_Count
    df['SYLLABLE PER WORD'] = syllable_per_word
    df['PERSONAL PRONOUNS'] = reasonable_pronouns
    df['AVG WORD LENGTH'] = average_Word_length
    
    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file_path, index=False)


# # HERE IS THE MAIN DRIVER CODE OF THE PROGRAM.

# In[17]:


# Define the paths(CHANGE THE PATH OF THE FILE ACCORDING TO YOUR LOCATION)
directory_path = 'C:/Users/Kirti/Desktop/web_scrape and analysis/Scraped_data/'
stopwords_folder = 'C:/Users/Kirti/Desktop/web_scrape and analysis/StopWords-20240619T074615Z-001'
excel_file_path = "C:/Users/Kirti/Desktop/Output folder/Output Data Structure(1).xlsx"

# Call the main function
read_files_in_directory(directory_path, stopwords_folder, excel_file_path)


# THIS IS THE FULL PYTHON CODE OF THE 
# 
# 
# 1.WEB SCRAPING 
# 2.TEXT ANALYSIS
# 
# WAITING FOR YOUR REPLY.THANK YOU.






