import requests
from .video import Video


class Channel:
    VLIVE_URI = 'https://api-vfan.vlive.tv/vproxy/channelplus/getChannelVideoList'
    VFAN_APP_ID = '8c6cc7b45d2568fb668be6e05b6e5a3b'
    MAX_NUM_LIST = 100

    def __init__(self, channel_seq, limit=1024, allow_other_channel=True, allow_mini_replay=True, search_word=''):
        self.channel_name = ''
        self.videos = []
        self.limit = limit
        self.allow_other_channel = allow_other_channel
        self.allow_mini_replay = allow_mini_replay
        self.search_word = search_word
        self.index = 0
        self.params = {
            'app_id': self.VFAN_APP_ID,
            'channelSeq': channel_seq,
            'maxNumOfRows': self.MAX_NUM_LIST,
            'pageNo': 1,
        }

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.can_stop_iteration():
                raise StopIteration
            if self.filter_video_data():
                break
        self.videos[self.index].generate_timestamp()
        content = self.videos[self.index]
        self.index += 1
        return content

    def fetch_videos(self):
        res = requests.get(self.VLIVE_URI, params=self.params)
        data = res.json()
        return data

    def configure_videos(self):
        data = self.fetch_videos()['result']
        self.channel_name = data['channelInfo']['channelName']
        try:
            for i in data['videoList']:
                self.videos.append(Video(i['videoSeq'], i['title'], i['representChannelName'], i['onAirStartAt']))
        except KeyError:
            return False
        self.params['pageNo'] += 1
        return True

    def filter_video_data(self):
        try:
            if (self.search_word == '' or self.search_word in self.videos[self.index].title) \
                    and (self.allow_mini_replay or '[CH+ mini replay]' not in self.videos[self.index].title) \
                    and (self.allow_other_channel or self.channel_name == self.videos[self.index].channel_name):
                return True
        except IndexError:
            return False
        self.index += 1
        self.limit += 1
        self.filter_video_data()

    def can_stop_iteration(self):
        if self.has_reached_limit():
            return True
        if self.index < len(self.videos):
            return False
        else:
            return not self.configure_videos()

    def has_reached_limit(self):
        if not self.index < self.limit:
            return True
        else:
            return False
