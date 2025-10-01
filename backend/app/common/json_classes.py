
class Oauth:
    google=None
    facebook=None
    twitter = None
    apple = None
    def __init__(self, google,facebook, twitter, apple):
        self.google = google
        self.facebook = facebook
        self.twitter = twitter
        self.apple = apple

    def to_json(self):
        return {
            'google': self.google,
            'facebook': self.facebook,
            'twitter': self.twitter,
            'apple': self.apple
        }