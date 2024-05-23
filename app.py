import streamlit as st
import preprocess
import stats
import matplotlib.pyplot as plt
import numpy as np

st.sidebar.title("WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocess.preprocess(data)

    user_list = df['User'].unique().tolist()
    if 'Group Notification' in user_list:
        user_list.remove('Group Notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    st.title("WhatsApp Chat Analysis for " + selected_user)
    if st.sidebar.button("Show Analysis"):
        num_messages, num_words, media_omitted, links = stats.fetchstats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(num_words)
        with col3:
            st.header("Media Shared")
            st.title(media_omitted)
        with col4:
            st.header("Links Shared")
            st.title(links)

        if selected_user == 'Overall':
            st.title('Most Busy Users')
            busycount, newdf = stats.fetchbusyuser(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(busycount.index, busycount.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(newdf)



        most_common_df = stats.getcommonwords(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.title('Most commmon words')
        st.pyplot(fig)

        st.title('Emoji Analysis')
        emoji_df = stats.getemojistats(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            emojicount = emoji_df['Count'].values
            perlist = [(i/sum(emojicount))*100 for i in emojicount]
            emoji_df['Percentage Use'] = np.array(perlist)
            st.dataframe(emoji_df)

        st.title("Monthly Timeline")
        time = stats.monthtimeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(time['Time'], time['Message'], color='green')
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        st.pyplot(fig)

        st.title("Activity Maps")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = stats.weekactivitymap(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)
        with col2:
            st.header("Most Busy Month")
            busy_month = stats.monthactivitymap(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)

        st.title('Sentiment Analysis')
        sentiment_df = stats.fetch_sentiment_analysis(selected_user, df)
        fig, ax = plt.subplots()
        ax.pie(sentiment_df['Count'], labels=sentiment_df['Sentiment'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
        st.dataframe(sentiment_df)

        st.title('Response Time Analysis (minutes)')
        response_time_df = stats.calculate_response_times(df)
        st.dataframe(response_time_df)

        fig, ax = plt.subplots()
        ax.bar(response_time_df['User'], response_time_df['AvgResponseTime'], color='blue')

        # Remove tick labels from the x-axis
        plt.xticks([])

        plt.xlabel('Users')  # This label will be hidden because there are no tick labels
        plt.ylabel('Average Response Time (minutes)')
        plt.title('Average Response Time')
        plt.tight_layout()
        st.pyplot(fig)