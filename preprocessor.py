import re
import pandas as pd
# import helper
import emoji

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def preprocess(data ):

    type= 'Android'
    if(data.startswith("[")):
        type = 'IOS'
    
    pattern = r"\[\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\s(?:AM|PM)\]" 

    if(type=='Android'):
        pattern = r"\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s?[ap]m\s-\s"

    messages = re.split(pattern,data)[1:]
    dates = re.findall(pattern,data)
    dates = [date.replace("\u202f", " ") for date in dates]
    df = pd.DataFrame({'user_message':messages , 'message_date':dates})

    # convert message_date type

    if(type=='IOS'):
        df['message_date'] = df['message_date'].str.strip("[]")
        df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M:%S %p")
    else :
        df['user_message'] = df['user_message'].str.lstrip('- ')
        df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M %p - ")

    df.rename(columns={'message_date': 'date'} , inplace=True)
    users = []
    messages= []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s',message)
        if(entry[1:]): #username
            users.append(entry[1])
            messages.append(entry[2])
        else :
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df['message'] = df['message'].str.replace('\u200e', '', regex=True)
    df['message'] = df['message'].str.strip() 
    df.drop(columns=['user_message'] , inplace =True)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df.date.dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['day_name'] = df.date.dt.day_name()
    df['only_date'] = df['date'].dt.date
    period =[]
    for hour in df[['day_name','hour']]['hour']:
        if hour==23:
            period.append(str(hour)+"-00")
        elif hour==0:
            period.append("00-"+str(hour+1))
        else :
            period.append(str(hour)+"-"+str(hour+1))
    df['period'] = period

    # Sentiment Analysis
    df['sentiment'] = df['message'].apply(get_sentiment)

    return df



def get_sentiment(text):
    text = emoji.demojize(text, delimiters=(" ", " "))
    scores = analyzer.polarity_scores(text)
    if scores["compound"] >= 0.05:
        return "Positive"
    elif scores["compound"] <= -0.05:
        return "Negative"
    else:
        return "Neutral"
