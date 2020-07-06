import json
import time
import requests


from random import uniform


def _check_artist_names(artist_names):
    if isinstance(artist_names, list):
        if all([isinstance(x, str) for x in artist_names]):
            return artist_names
        else:
            raise AttributeError('all artist names in list must be str')
    elif isinstance(artist_names, str):
        return [artist_names]
    elif artist_names is None:
        return None
    else:
        raise AttributeError('artist_names must be list or str')


def _check_artist_ids(artist_ids):
    if isinstance(artist_ids, list):
        if all([isinstance(x, int) for x in artist_ids]):
            return artist_ids
        else:
            raise AttributeError('all artist ids in list must be int')
    elif isinstance(artist_ids, int):
        return [artist_ids]
    elif artist_ids is None:
        return None
    else:
        raise AttributeError('artist_names must be list or int')


class VkApi:

    def __init__(self, token, artist_names=None, artist_ids=None):
        """
        Инициализация экземпляра класса

        :param token:           str, токен с доступом ads
        :param artist_names:    list or str, список или одно имя исполнителя
        :param artist_names:    list or int, список или одна айдишка исполнителя
        """
        self.session = requests.session()
        self.token = token
        self.account_id = self._get_account_id()
        self.link_url = self._get_link_url()
        self.artist_names = _check_artist_names(artist_names)
        self.artist_ids = _check_artist_ids(artist_ids)

    def _get_account_id(self):
        """
        Возвращает айди личного рекламного кабинета (нужно для получения размера аудиторий)

        :return: int
        """
        url = f'https://api.vk.com/method/ads.getAccounts?access_token={self.token}&v=5.110'
        resp = self.session.get(url).json()
        try:
            cabinets = resp['response']
            for cab in cabinets:
                if cab['account_type'] == 'general':
                    return cab['account_id']
        except KeyError:
            print(resp)

    def _get_link_url(self):
        """
        Возвращает ссылку на первый паблик, к которому есть админский или рекламный доступ
        (нужно для получения размера аудиторий)

        :return:
        """
        url = f'https://api.vk.com/method/groups.get?access_token={self.token}&v=5.110&filter=admin,advertiser'
        resp = self.session.get(url).json()
        try:
            group_id = resp['response']['items'][0]
            return f'https://vk.com/public{group_id}'
        except (KeyError, IndexError):
            print(resp)

    def get_artists_ids(self, artist_names=None):
        """
        Возвращает словарь с айдишками артистов. Это не те же самые айдишки, что в методах audio

        :param artist_names:    list or str
        :return:                dict, {artist_name: artist_id}
        """
        if artist_names is not None:
            self.artist_names = _check_artist_names(artist_names)
        else:
            if self.artist_names is None:
                raise AttributeError('artist_name attribute necessarily need to get_artist_ids')

        artist_ids = {}
        for name in self.artist_names:
            url = f'https://api.vk.com/method/ads.getMusicians?access_token={self.token}&v=5.110&artist_name={name}'
            resp = self.session.get(url).json()
            try:
                founded_artists = resp['response']['items']
                for artist in founded_artists:
                    if artist['name'].lower() == name.lower():
                        artist_ids[artist['name']] = artist['id']
                        break
            except KeyError:
                print(resp)
            time.sleep(uniform(0.4, 0.5))

        return artist_ids

    def get_audience_count_by_artist_ids(self, artist_ids=None):
        """
        Возвращает словарь с размерами аудиторий артистов по их айдишкам

        :param artist_ids:  list or int
        :return:            dict, {artist_id, audience_count}
        """
        if artist_ids is not None:
            self.artist_ids = _check_artist_ids(artist_ids)
        else:
            if self.artist_ids is None:
                raise AttributeError('artist_ids attribute necessarily need to get_audience_count')

        audience_count = {}
        for artist_id in self.artist_ids:
            criteria = json.dumps({'music_artists_formula': artist_id})
            url = f'https://api.vk.com/method/ads.getTargetingStats?access_token={self.token}&v=5.110' \
                  f'&account_id={self.account_id}&link_url={self.link_url}&criteria={criteria}'
            resp = self.session.get(url).json()
            try:
                count = resp['response']['audience_count']
                audience_count[artist_id] = count
            except KeyError:
                print(resp)
            time.sleep(uniform(0.4, 0.5))

        return audience_count

    def get_audience_count_by_artist_name(self, artist_names):
        """
        Возвращает словарь с размерами аудиторий артистов по их именам

        :param artist_names:    list or str
        :return:                dict, {artist_name: audience_count}
        """
        if artist_names is not None:
            self.artist_names = _check_artist_names(artist_names)
        else:
            if self.artist_names is None:
                raise AttributeError('artist_name attribute necessarily need to get_artist_ids')

        audience_count = {}
        for name in self.artist_names:
            url = f'https://api.vk.com/method/ads.getMusicians?access_token={self.token}&v=5.110&artist_name={name}'
            resp = self.session.get(url).json()
            try:
                founded_artists = resp['response']['items']
                for artist in founded_artists:
                    if artist['name'].lower() == name.lower():
                        artist_id = artist['id']
                        count = self.get_audience_count_by_artist_ids(artist_id)[artist_id]
                        audience_count[name] = count
                        break
            except KeyError:
                print(resp)

            time.sleep(uniform(0.4, 0.5))

        return audience_count

