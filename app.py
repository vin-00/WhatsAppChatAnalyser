import streamlit as st
import preprocessor , helper
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

import random

st.set_page_config(
    page_title="WhatsAppChat Analyser",  # Title of the browser tab
    page_icon="whatsapp.png",  # Emoji as favicon
    layout="wide"  # Optional: Use "centered" or "wide"
)

st.title("WhatsApp Chat Analytics")

st.sidebar.title("Whatsapp Chat Analyzer") 
uploaded_file = st.sidebar.file_uploader("Choose a file" , key='uploaded_file')

if uploaded_file is not None :
    bytes_data= uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data )

    # Fetch Unique users
    user_list = df['user'].unique().tolist()
    
    group_name = "-1"
    
    if(len(user_list)>2):
        group_name = user_list.pop(0)
    
    user_list.sort()

    if(group_name!='-1'):
        df = df[df['user']!=group_name]
    
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show Analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        st.title("Top Statistics")
        num_messages , word ,media ,links , deleted , longest_msg= helper.fetch_stats(selected_user, df)
        col1 , col2 , col3 = st.columns(3)
        with col1 :    
            st.header("Total Messages")
            st.title(num_messages)

        with col2 :    
            st.header("Total Words")
            st.title(word)

        with col3 :    
            st.header("Media Shared")
            st.title(media)

        col1 ,col2,col3 = st.columns(3)
        with col1 :    
            st.header("Links Shared")
            st.title(links)
        with col2 :
            st.header("Messages Deleted")
            st.title(deleted)
        with col3 :
            st.header("Longest Message")
            st.title(longest_msg)


        st.write("---")
        # Sentiment Analysis

        st.title("Sentiment Analysis")

        sent = helper.filter_df(df,selected_user)

        if(selected_user=='Overall'):
            most_positive , most_negative = helper.toxic_friendly(sent)
            
            st.subheader(f"Most Friendly User : {most_positive}")
            st.subheader(f"Most Toxic User: {most_negative}")

        fig , ax = plt.subplots()
        fig.patch.set_facecolor("#0E1117")  
        ax.set_facecolor("#0E1117")
        sns.countplot(data= sent, x='sentiment', ax=ax, order=['Positive','Negative','Neutral'],hue='sentiment', palette="magma", legend = False)

        plt.xticks(rotation='horizontal')
        ax.tick_params(colors="white")  # Change axis ticks color
        ax.xaxis.label.set_color("white")  # X-axis label color
        ax.yaxis.label.set_color("white")  # Y-axis label color
        ax.spines["bottom"].set_color("white")  # Make bottom border white
        ax.spines["left"].set_color("white")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        st.pyplot(fig)


        # Longest Streak
        st.title("Longest Streak")
        max_streaks = helper.get_streak(selected_user,df)

        max_streak_value = max_streaks["max_streak"].max()
        for _, row in max_streaks.iterrows():
            user = row["user"]
            streak = row["max_streak"]
            normalized_width = (streak / max_streak_value) * 100
            
            st.header(user+" :  "+str(streak)+" days")
            st.markdown(
                f"""
                <div style="
                    width: {normalized_width}%;
                    background-color: #e0e0e0;
                    border-radius: 10px;
                    height: 20px;
                    position: relative;
                    margin-bottom: 25px;
                ">
                    <div style="
                        width: 100%;
                        background: linear-gradient(90deg, #FF5733, #FF8D1A);
                        height: 100%;
                        border-radius: 10px;
                    "></div>
                </div>
                """,
                unsafe_allow_html=True
            )


        # Timeline

        col1  ,col2 = st.columns(2)

        timeline , daily = helper.monthly_timeline(selected_user,df)
        with col1 : 

            st.title("Monthly Timeline")
            fig , ax = plt.subplots()
            fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
            ax.set_facecolor("#0E1117")
            sns.lineplot(x=timeline.time, y=timeline.message, ax=ax , color='gold')

            plt.xticks(rotation='vertical')
            ax.tick_params(colors="white")  # Change axis ticks color
            ax.xaxis.label.set_color("white")  # X-axis label color
            ax.yaxis.label.set_color("white")  # Y-axis label color
            ax.spines["bottom"].set_color("white")  # Make bottom border white
            ax.spines["left"].set_color("white")
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            st.pyplot(fig)

        with col2 : 
            st.title("Daily Timeline")
            fig , ax = plt.subplots()
            fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
            ax.set_facecolor("#0E1117")
            sns.lineplot(x=daily.only_date, y=daily.message, ax=ax , color='gold')

            plt.xticks(rotation='vertical')
            ax.tick_params(colors="white")  # Change axis ticks color
            ax.xaxis.label.set_color("white")  # X-axis label color
            ax.yaxis.label.set_color("white")  # Y-axis label color
            ax.spines["bottom"].set_color("white")  # Make bottom border white
            ax.spines["left"].set_color("white")
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            st.pyplot(fig)
        
        # Busy day and month
        col1 , col2 = st.columns(2)

        with col1 : 
            st.title("Most Busy Day")
            days = helper.day_activity(selected_user,df)

            fig , ax = plt.subplots()
            fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
            ax.set_facecolor("#0E1117")
            sns.barplot(x=days.index, y=days.values, ax=ax, hue=days.index, palette="coolwarm", legend = False)

            plt.xticks(rotation='vertical')
            ax.tick_params(colors="white")  # Change axis ticks color
            ax.xaxis.label.set_color("white")  # X-axis label color
            ax.yaxis.label.set_color("white")  # Y-axis label color
            ax.spines["bottom"].set_color("white")  # Make bottom border white
            ax.spines["left"].set_color("white")
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            st.pyplot(fig)

        with col2 :
            st.title("Most Busy Month")
            months = helper.month_activity(selected_user,df)

            fig , ax = plt.subplots()
            fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
            ax.set_facecolor("#0E1117")
            sns.barplot(x=months.index, y=months.values, ax=ax, hue=months.index, palette="coolwarm", legend = False)

            plt.xticks(rotation='vertical')
            ax.tick_params(colors="white")  # Change axis ticks color
            ax.xaxis.label.set_color("white")  # X-axis label color
            ax.yaxis.label.set_color("white")  # Y-axis label color
            ax.spines["bottom"].set_color("white")  # Make bottom border white
            ax.spines["left"].set_color("white")
            ax.set_xlabel("")
            ax.set_ylabel("")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            st.pyplot(fig)

        #  Active users 
        if(selected_user=='Overall'):
            
            st.title("Most Active Users")
            x , y= helper.most_busy_users(df)
            
            
            col1 , col2 = st.columns(2)

            with col1 :
                fig , ax = plt.subplots()
                fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
                ax.set_facecolor("#0E1117")
                sns.barplot(x=x.index, y=x.values, ax=ax,hue=x.index , palette="magma", legend = False)

                plt.xticks(rotation='vertical')
                ax.tick_params(colors="white")  # Change axis ticks color
                ax.xaxis.label.set_color("white")  # X-axis label color
                ax.yaxis.label.set_color("white")  # Y-axis label color
                ax.spines["bottom"].set_color("white")  # Make bottom border white
                ax.spines["left"].set_color("white")
                ax.set_xlabel("")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

                st.pyplot(fig)
            with col2 :
                colors = sns.color_palette("magma", len(y))
                fig, ax = plt.subplots(facecolor="#0E1117")
                fig.patch.set_facecolor("#0E1117")
                ax.set_facecolor("#0E1117")
                ax.pie(y['count'], labels=y['user'], autopct='%1.1f%%', startangle=140 ,colors = colors ,textprops={"color":"white"})
                st.pyplot(fig)


        st.write("---")
        # Activity Map
        st.title("Activity Map")

        fig , ax = plt.subplots(figsize=(22,8))
        fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
        ax.set_facecolor("#0E1117")

        user_heatmap = helper.activity_heatmap(selected_user,df)
        
        ax = sns.heatmap(user_heatmap , cmap="magma")

        plt.yticks(rotation=0)
        plt.xticks(rotation=90)
        ax.tick_params(colors="white",labelsize=16)  
        ax.xaxis.label.set_color("white")  
        ax.yaxis.label.set_color("white")  
        ax.spines["bottom"].set_color("white")  
        ax.spines["left"].set_color("white")
        ax.set_xlabel("")
        ax.set_ylabel("")
        cbar = ax.collections[0].colorbar
        cbar.ax.yaxis.set_tick_params(color="white")  
        plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white") 
        
        st.pyplot(fig)

        # WordCloud

        st.title("Word Cloud")

        df_wc = helper.create_word_cloud(selected_user,df)

        if(df_wc=='Empty'):
            st.write("Not Enough Words to create Word Cloud")
        
        else:
            fig,ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig) 

        # Most Common words
        st.title("Most Used Words")
        most_common_df = helper.most_common_words(selected_user,df)

        if(len(most_common_df)==0):
            st.write("Not enough words")
        else:
            fig , ax = plt.subplots()

            # Styling the graph 
            fig.patch.set_facecolor("#0E1117")  # Set entire figure background to black
            ax.set_facecolor("#0E1117")
            sns.barplot(y=most_common_df[0],x=most_common_df[1],hue=most_common_df[0], ax=ax,palette='viridis',legend=False)

            ax.set_xlabel("")
            ax.set_ylabel("")
            plt.xticks(rotation='vertical')
            ax.tick_params(colors="white")  
            ax.xaxis.label.set_color("white")  # X-axis label color
            ax.yaxis.label.set_color("white")  # Y-axis label color
            ax.spines["bottom"].set_color("white")  
            ax.spines["left"].set_color("white")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            st.pyplot(fig) 

        # Emoji Analysis

        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        if(len(emoji_df)==0):
            st.write("No emojis present")
        
        else:
            size = 150  
            st.title("These are the most used emojis:")

            emoji_html = "<div style='white-space: nowrap;'>"
            rank =1
            for _, row in emoji_df.iterrows():
                emoji_html += f'<span style="font-size:{size}px; margin-right: 10px;">{rank}.{row[0]}</span>'
                size-=30
                rank+=1
                if(size==0):
                    break
            emoji_html += "</div>"

            st.markdown(emoji_html, unsafe_allow_html=True)

st.markdown("---")  # Adds a horizontal line

st.markdown("© 2025 WhatsApp Chat Analyser | Built with ❤️ by Vinay Khatri")
        

