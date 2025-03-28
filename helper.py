
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji


extract = URLExtract()
def fetch_stats(selected_user , df):

    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    # Media
    media = df[df['message'].str.contains("omitted", case=False, na=False)].shape[0] # It checks for image , audio , video , document , sticker and GIF .
    # Links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    
    # Deleted Messages
    deleted = df[(df['message'].str.contains("message was deleted", case=False, na=False)) | (df['message'].str.contains("You deleted this message", case=False, na=False))].shape[0]

    # Longest message
    longest_msg = 0;
    for msg in  df['message']:
        # removing white spaces
        msg = msg.strip()  
        msg = " ".join(msg.split())
        if(len(msg)>longest_msg):
            longest_msg = len(msg)

    return num_messages , len(words) ,media , len(links) , deleted ,longest_msg

def most_busy_users(df):
    x= df['user'].value_counts().head()
    y = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().head()

    return x , y

def create_word_cloud(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    wc = WordCloud(width=500, height=500 , min_font_size=10 , background_color = 'white')
    df = df[~df['message'].str.contains("omitted", case=False, na=False)]

    f = open("stop_hinglish.txt","r")
    stop = f.read()

    def remove_stop_words(message):
        y = []
        for word in message.lower().split() :
            if word not in stop:
                y.append(word)
        return " ".join(y)

    df['message'].apply(remove_stop_words)

    if(df['message'].empty):
        return "Empty"
    
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user , df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    f = open('stop_hinglish.txt','r')
    stop_words = f.read()
    words = []
    df = df[~df['message'].str.contains("omitted", case=False, na=False)]
    for message in df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_used = pd.DataFrame(Counter(words).most_common(20))
    return most_used

def emoji_helper(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user'] == selected_user]

    emojis = []
    excluded_emojis = {"🥲" ,'🥹','🥹🥹'} 
    def is_valid_emoji(c):
        return emoji.is_emoji(c) and c not in excluded_emojis and "\\U" not in repr(c)

    for message in df['message']:
        emojis.extend([c for c in message if is_valid_emoji(c)])
    
    return pd.DataFrame(Counter(emojis).most_common(20))

def monthly_timeline(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    timeline = df.groupby(['year','month']).count()['message'].reset_index()
    daily = df.groupby('only_date').count()['message'].reset_index()
    time=[]
    for i in range(len(timeline)):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))
    timeline['time'] =time

    return timeline ,daily

def day_activity(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    days = df['day_name'].value_counts()
    return days

def month_activity(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    months = df['month'].value_counts()
    return months

def activity_heatmap(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]

    pivot_table = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)

    return pivot_table

def get_streak(selected_user,df):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    
    user_max_streaks = {}  

    for user in df["user"].unique():
        user_df = df[df["user"] == user]  
        user_df = user_df.sort_values(by=["date"],ascending=False)
        user_df["diff"] = user_df["date"].diff().dt.days
        max_streak = 0
        current_streak = 0
        user_df = user_df.drop_duplicates("only_date")
        for diff in user_df["diff"]:
            if diff == -1:  
                current_streak += 1
            else:  
                current_streak = 1  
            
            max_streak = max(max_streak, current_streak)  
        
        user_max_streaks[user] = max_streak  

    max_streak_df = pd.DataFrame(user_max_streaks.items(), columns=["user", "max_streak"]).reset_index()
    max_streak_df.sort_values(by=['max_streak'],ascending=False, inplace=True)
    return max_streak_df.head()

def filter_df(df,selected_user):
    if(selected_user!='Overall'):
        df = df[df['user']==selected_user]
    df = df[~(df['message'].str.contains("omitted", case=False, na=False))]
    return df