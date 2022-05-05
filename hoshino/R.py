import os
from urllib.parse import urljoin
from urllib.request import pathname2url

import nonebot
from nonebot.adapters.onebot.v11 import MessageSegment
from PIL import Image

from hoshino import util

logger = nonebot.logger
config = nonebot.get_driver().config


class ResObj:
    def __init__(self, res_path):
        res_dir = config.RES_DIR  # fixme: 别在用户目录搞事啊 用os.getcwd吧
        fullpath = os.path.abspath(os.path.join(res_dir, res_path))
        if not fullpath.startswith(os.path.abspath(res_dir)):
            raise ValueError('Cannot access outside RESOUCE_DIR')
        self.__path = os.path.normpath(res_path)

    @property
    def url(self):
        """资源文件的url，供酷Q（或其他远程服务）使用"""
        return urljoin(config.RES_URL, pathname2url(self.__path))

    @property
    def path(self):
        """资源文件的路径，供bot内部使用"""
        return os.path.join(config.RES_DIR, self.__path)

    @property
    def exist(self):
        return os.path.exists(self.path)


class ResImg(ResObj):
    @property
    def cqcode(self) -> MessageSegment:
        if config.RES_PROTOCOL == 'http':
            return MessageSegment.image(self.url)
        elif config.RES_PROTOCOL == 'file':
            return MessageSegment.image(f'file:///{os.path.abspath(self.path)}')
        else:
            try:
                return MessageSegment.image(util.pic2b64(self.open()))
            except Exception as e:
                logger.exception(e)
                return MessageSegment.text('[图片出错]')

    def open(self) -> Image:
        try:
            return Image.open(self.path)
        except FileNotFoundError:
            logger.error(f'缺少图片资源：{self.path}')
            raise


class ResRec(ResObj):
    @property
    def cqcode(self) -> MessageSegment:
        if config.RES_PROTOCOL == 'http':
            return MessageSegment.record(self.url)
        elif config.RES_PROTOCOL == 'file':
            return MessageSegment.record(f'file:///{os.path.abspath(self.path)}')


def get(path, *paths):
    return ResObj(os.path.join(path, *paths))


def img(path, *paths):
    return ResImg(os.path.join('img', path, *paths))


def rec(path, *paths):
    return ResRec(os.path.join('record', path, *paths))
