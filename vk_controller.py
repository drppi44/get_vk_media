from uuid import uuid4

import vk_api


class VKController:
    def __init__(self, login, password):
        vk_session = vk_api.VkApi(login, password, app_id=2685278)
        vk_session.auth()
        self.vk = vk_session.get_api()

    def get_conversations(self):
        offset = 0
        count = 50
        conversations = []

        while True:
            response = self.vk.messages.getConversations(filter='all', offset=offset, count=count)
            conversations += response['items']
            total_count = response['count']
            offset += count

            if offset >= total_count:
                break

        return conversations

    def get_conversation_photos_and_videos(self, conversation):
        peer_id = conversation['conversation']['peer']['id']
        offset = 0
        count = 200
        videos = []
        photos = []

        while True:
            response = self.vk.messages.getHistory(peer_id=peer_id, count=count, offset=offset)
            messages = response['items']

            for message in messages:
                if 'attachments' in message:
                    attachments = message['attachments']
                    for attachment in attachments:
                        if attachment['type'] == 'photo':
                            photo_sizes = attachment['photo']['sizes']
                            largest_size = max(photo_sizes, key=lambda x: x['width'] * x['height'])
                            photo_url = largest_size['url']
                            photos.append(photo_url)
                        elif attachment['type'] == 'video':
                            if attachment.get('video', {}).get('platform') == 'YouTube':
                                continue

                            video_response = self.vk.video.get(videos=f'{attachment["video"]["owner_id"]}'
                                                                      f'_{attachment["video"]["id"]}'
                                                                      f'_{attachment["video"].get("access_key", "")}')

                            if not video_response['items'] or 'player' not in video_response['items'][0]:
                                continue

                            videos.append(video_response['items'][0]['player'])

            if len(messages) < count:
                break

            offset += count

        return photos, videos

    def get_user_name(self, conversation):
        try:
            user_info = self.vk.users.get(user_ids=conversation['conversation']['peer']['id'])[0]
            return f'{user_info["first_name"]} {user_info["last_name"]}'
        except IndexError:
            return str(uuid4())