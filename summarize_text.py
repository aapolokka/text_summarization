import os
import re
import PyPDF2
import spacy
import argparse
from collections import defaultdict

# Function to find text between certain chapters
def extract_text_between_pdf_sections(pdf_file, start_section, end_section):
    
    # Read PDF file
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        start_found = False
        for i in range(len(reader.pages)):
            page_text = reader.pages[i].extract_text()
            if re.search(start_section, page_text):
                start_found = True
            if start_found:
                text += page_text
                if re.search(end_section, page_text):
                    break
        
        # Extract text between the section and the next chapter
        start_match = re.search(start_section, text)
        end_match = re.search(end_section, text)
        if start_match and end_match:
            text = text[start_match.end():end_match.start()]
        return text


# Function to summarize the text
def summarize(text):

    nlp = spacy.load("en_core_web_lg")

    # Clean text
    cleaned_text = ' '.join(text.split())

    # Sentence tokenization
    doc = nlp(cleaned_text)
    sentences = []
    for s in doc.sents:
        sentences.append(s.text)

    # Word tokenization and word-frequency table
    word_freq = defaultdict(int)
    # Words in document
    for word in doc:
        if word.text.lower() not in nlp.Defaults.stop_words and not word.is_punct:
            word_freq[word.text.lower()] += 1

    # Summarization
    ranking = defaultdict(int)
    for i, sentence in enumerate(sentences):
        for word in nlp(sentence.lower()):
            if word.text in word_freq:
                ranking[i] += word_freq[word.text]
    indexes = sorted(ranking, key=ranking.get, reverse=True)[:5]
    
    # Write summary
    summary = ''
    for i in sorted(indexes):
        summary += sentences[i] + ' '

    return summary

def main():
    
    # Argparser to help run code from terminal
    parser = argparse.ArgumentParser(description='List of options')
    parser.add_argument('-f', '--file' ,dest='infile', help='Name of input PDF file', required=True)
    parser.add_argument('-s', '--start', dest='start', help='Name of first PDF section | format: \'start\'', required=True)
    parser.add_argument('-e', '--end', dest='end', help='Name of second PDF section | format: \'end\'', required=True)
    
    args = parser.parse_args()
    start = args.start
    end = args.end
    pdf_file = args.infile

    text = extract_text_between_pdf_sections(pdf_file, str(start), str(end))
    summary = summarize(text)

    print("Summary:")
    print(summary)

if __name__ == '__main__':
    main()
