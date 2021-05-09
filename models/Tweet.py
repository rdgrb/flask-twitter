from app import db

class Tweet(db.Model):
    __tablename__ = "TB_TWEET"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    id_user = db.Column(db.Integer, db.ForeignKey("TB_USER.id"))
    tweet = db.Column(db.String(280))
    tweeted_at = db.Column(db.DateTime)

    def __init__(self, id_user, tweet, tweeted_at):
        self.id_user = id_user
        self.tweet = tweet
        self.tweeted_at = tweeted_at 
