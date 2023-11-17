import requests
import csv
import pandas as pd
import smtplib
import ssl

def get_facebook_comments(page_id, access_token):
    base_url = f'https://graph.facebook.com/v13.0/{page_id}/posts'
    params = {
        'fields': 'comments{id,message,created_time,from}',
        'access_token': access_token,
    }

    comments_list = []

    # Fetch posts
    response = requests.get(base_url, params=params)
    data = response.json()

    # Extract comments
    for post in data['data']:
        if 'comments' in post:
            comments = post['comments']['data']
            comments_list.extend(comments)

    while 'paging' in data and 'next' in data['paging']:
        # Fetch next page of posts
        response = requests.get(data['paging']['next'])
        data = response.json()

        # Extract comments
        for post in data['data']:
            if 'comments' in post:
                comments = post['comments']['data']
                comments_list.extend(comments)

    return comments_list

def save_comments_to_csv(comments, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['comment_id', 'message', 'created_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for comment in comments:
            writer.writerow({
                'comment_id': comment['id'],
                'message': comment.get('message', ''),
                'created_time': comment['created_time']
                #'from_name': comment['from']['name']
            })

if __name__ == '__main__':
    page_id = 'Brands fb page id'
    access_token = 'API Access Token'
    csv_filename = 'fb_comment.csv'

    comments = get_facebook_comments(page_id, access_token)
    save_comments_to_csv(comments, csv_filename)

# Replace 'your_file.csv' with the actual path to your CSV file
file_path = 'fb_comment.csv'

# Replace 'desired_column' with the name of the column you want to select
desired_column = 'message'

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Select the desired column
selected_column = df[desired_column].tolist()

# Base sentimental score of site
sscore=10
m_message=[]
score2=''

# Now, 'selected_column' contains the data from the specified column
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Iterate through each sentence in the list

analyzer = SentimentIntensityAnalyzer()
for sentence in selected_column:
    vs = analyzer.polarity_scores(sentence)
    print("{:-<65} {}".format(sentence, str(vs)))

    max_value = max(vs['neg'], vs['pos'], vs['neu'])
    #print(max_value)
    
    # Find the key for the specified value
    matching_keys = [key for key, value in vs.items() if value == max_value]

    #print(f"The maximum value in the dictionary is: {matching_keys}")
    if matching_keys==['neg']:
        sscore=(sscore-max_value) 
    elif matching_keys==['pos']:
        sscore=(sscore+max_value)
    else:
        sscore=(sscore)
    m_message.append(sentence)


score2=str(sscore)
m_score=score2[:6]
mail_mssge=str(m_message[:5:])

from email.message import EmailMessage

# Define email sender and receiver
email_sender = 'sender email'
email_password = 'sender email password'
email_receiver = 'receiver email'

# Set the subject and body of the email
subject = 'Sentimental Score Analyzer!'
body = """Current Sentimental Score of your page is:""" + m_score +""". 
Reason for last updatation in score are due to following comment: """ + mail_mssge

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

# Add SSL (layer of security)
context = ssl.create_default_context()

# Log in and send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())
