from urlextract import URLExtract
import pandas as pd
import re
from textblob import TextBlob

extract = URLExtract()


def analyze_sentiment(message):
    """
    Analyze the sentiment of a given message.

    Args:
        message (str): The message to analyze.

    Returns:
        str: The sentiment of the message ('Positive', 'Negative', 'Neutral').
    """
    analysis = TextBlob(message)
    if analysis.sentiment.polarity > 0:
        return 'Positive'
    elif analysis.sentiment.polarity < 0:
        return 'Negative'
    else:
        return 'Neutral'

def fetch_sentiment_analysis(selected_user, df):
    """
    Fetch the sentiment analysis for the selected user or overall chat.

    Args:
        selected_user (str): The user to fetch sentiment analysis for.
        df (DataFrame): The chat DataFrame.

    Returns:
        DataFrame: DataFrame with sentiment analysis results.
    """
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    df['Sentiment'] = df['Message'].apply(analyze_sentiment)
    sentiment_counts = df['Sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']

    return sentiment_counts
def fetchstats(selected_user, df):

    # if the selected user is a specific user,then make changes in the dataframe,else do not make any changes

    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['Message']:
        words.extend(message.split())

    # counting the number of media files shared

    mediaommitted = df[df['Message'] == '<Media omitted>']

    # number of links shared

    links = []
    for message in df['Message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), mediaommitted.shape[0], len(links)


# most busy users {group level}

def fetchbusyuser(df):

    df = df[df['User'] != 'Group Notification']
    count = df['User'].value_counts().head()

    newdf = pd.DataFrame((df['User'].value_counts()/df.shape[0])*100)
    return count, newdf


from collections import Counter







# get most common words,this will return a dataframe of
# most common words

def getcommonwords(selecteduser, df):

    # getting the stopwords

    file = open('stop_hinglish.txt', 'r')
    stopwords = file.read()
    stopwords = stopwords.split('\n')

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    temp = df[(df['User'] != 'Group Notification') |
              (df['User'] != '<Media omitted>')]

    words = []

    for message in temp['Message']:
        for word in message.lower().split():
            if word not in stopwords:
                words.append(word)

    mostcommon = pd.DataFrame(Counter(words).most_common(20))
    return mostcommon


# Word cloud


def getemojistats(selecteduser, df):
    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    emojis = []
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    for message in df['Message']:
        emojis.extend(emoji_pattern.findall(message))

    emojidf = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))), columns=['Emoji', 'Count'])
    return emojidf


def monthtimeline(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    temp = df.groupby(['Year', 'Month_num', 'Month']).count()[
        'Message'].reset_index()

    time = []
    for i in range(temp.shape[0]):
        time.append(temp['Month'][i]+"-"+str(temp['Year'][i]))

    temp['Time'] = time

    return temp


def monthactivitymap(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    return df['Month'].value_counts()


def weekactivitymap(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    return df['Day_name'].value_counts()

def calculate_response_times(df):
    df['DateTime'] = pd.to_datetime(df['Date'])
    df['ResponseTime'] = df['DateTime'].diff().shift(-1)
    df['ResponseTime'] = df['ResponseTime'].dt.total_seconds() / 60.0  # convert to minutes

    response_time_df = df.groupby('User')['ResponseTime'].mean().reset_index()
    response_time_df.columns = ['User', 'AvgResponseTime']
    response_time_df = response_time_df.dropna()

    # Convert AvgResponseTime to always positive
    response_time_df['AvgResponseTime'] = response_time_df['AvgResponseTime'].abs()

    return response_time_df