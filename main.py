import json, os, sys, time, csv, tweepy

def setup_api():
    auth = tweepy.OAuthHandler(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])
    auth.set_access_token(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth)

def load_dagritme_data(current_day):
    filename = 'dagritme_data/dagritme_data_%s.csv'%current_day
    activities = []
    times = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            times.append(row['time'])
            activities.append(row['activity'])
    return times, activities

def generate_tweet():
    # Load daily routine data
    current_day = time.ctime()[:3].lower()
    times, activities = load_dagritme_data(current_day)
    # Get current time in the right timezone
    gm_shift = 2
    current_hour = '%02d'%(time.gmtime().tm_hour+gm_shift)
    current_minute = '%02d'%(time.gmtime().tm_min)
    hrmin = current_hour + current_minute
    print('Current day is %s time is %s:%s'%(current_day,current_hour,current_minute))
    # Any activities here?
    timediffs = [abs(int(i)-int(hrmin)) for i in times]
    act_index = list(filter(lambda x: x<=5, timediffs))
    if len(act_index)==1:
        activity = activities[timediffs.index(act_index[0])]
        print('Found activity: %s'%activity)
        tweet_text = 'Het is %s:%s, dus ik ga %s. Doe je mee in mijn #dagritme? Stuur me een berichtje of foto van jouw activiteit!'%(
            current_hour,current_minute,activity.lower())
        return tweet_text
    else:
        return None

def dagritme_tweet():
    api = setup_api()
    tweet_text = generate_tweet()
    if tweet_text is None:
        print('No activity found for this time.')
        gm_shift = 2
        current_hour = str(time.gmtime().tm_hour+gm_shift)
        current_minute = str(time.gmtime().tm_min)
        return 'Geen dagritmetweet geplaatst om %s:%s.'%(current_hour,current_minute)
    else:
        status = api.update_status(status=tweet_text)
        return 'Dagritmetweet geplaatst:\n\n%s'%tweet_text

def handler(event, context):
    response = dagritme_tweet()
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
