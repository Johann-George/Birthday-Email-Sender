# import required packages
import pandas as pd
import datetime
import smtplib
import time
from pymysql import NULL
from win10toast import ToastNotifier
from sqlalchemy import create_engine


# your gmail credentials here
from credentials import GMAIL_ID, GMAIL_PWD

# for desktop notification
toast = ToastNotifier()

def sendEmail(to, sub, msg):
    try:
        # connection to gmail
        gmail_obj = smtplib.SMTP('smtp.gmail.com', 587)

        # starting the session
        gmail_obj.starttls()

        # login using credentials
        gmail_obj.login(GMAIL_ID, GMAIL_PWD)

        # sending email
        gmail_obj.sendmail(GMAIL_ID, to,
                    f"Subject : {sub}\n\n{msg}")

        # quit the session
        gmail_obj.quit()

        print("Email sent to " + str(to) + " with subject "
            + str(sub) + " and message :" + str(msg))
        #code for notification
        toast.show_toast("Email Sent!" ,
                        f"{str(item['name'])} was sent an e-mail",
                        threaded = True,
                        icon_path = None,
                        duration = 6)

        while toast.notification_active():
            time.sleep(0.1)

    except smtplib.SMTPException as e:
        print("Failed to send email:", e)
        raise e
# driver code
if __name__ == "__main__":
    hostname = "127.0.0.1"  
    password = "Database$123"
    try:
        # create engine to connect to MySQL database using SQLAlchemy
        engine = create_engine(f'mysql+mysqlconnector://root:{password}@{hostname}/hbd')
        if(engine!=NULL):
            print("Connected to database")
        # read the data from MySQL table
        dataframe = pd.read_sql("SELECT * FROM data_values", engine)

        # Convert 'birthday' column to datetime data type
        dataframe['birthday'] = pd.to_datetime(dataframe['birthday'])

        # today date in format : DD-MM
        today = datetime.datetime.now().strftime("%d-%m")
        print(today)
        # current year in format : YY
        yearNow = datetime.datetime.now().strftime("%Y")
        print(yearNow)

        # Filter the dataframe to keep only the rows with birthday today
        today_birthday_df = dataframe[dataframe['birthday'].dt.strftime("%d-%m") == today]

        # Access the 'name' column values for individuals with birthday today
        name = today_birthday_df['name'].values.tolist()

        # Print the retrieved 'name' values
        print("Retrieved 'name' values of individuals with birthday today:",name)


        # writeindex list
        writeInd = []

        for index, item in dataframe.iterrows():
            
            msg = "Happy birthday "+str(item['name'])+ ". May this special day bring you lots of joy and happiness. On this occasion, I just want to remind you how much your friendship means to me and how grateful I am to have you in my life. Enjoy your day to the fullest!" 

            # Convert birthday Timestamp object to string
            bday = item['birthday'].strftime("%d-%m")

            # Check if current date matches the birthday date
            if bday == today:
                print("The value of name is ",str(item['name']))
                to = str(item['email'])
                sub = "Birthday Wishes"
                sendEmail(to, sub, msg)
                writeInd.append(index)

        # Update the 'sent' column for the rows where birthday emails were sent
        dataframe.loc[writeInd, 'sent'] = 'Y'

        # Update the MySQL table with the updated dataframe
        dataframe.to_sql('data_values', engine, if_exists='replace', index=False)
    
    except Exception as e:
        print("Failed to connect to the database:", e)
        raise e

            