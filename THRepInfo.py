import json
import os
import hashlib
import argparse

import threp
from PIL import Image, ImageDraw, ImageFont


def generateImage(rpy, dest):
    width, height = 480, 640

    rep = threp.THReplay(rpy)
    dirname = os.path.dirname(rpy)
    basename = os.path.basename(rpy).split('.')[0]

    gameid = basename.split('_')[0]

    games = json.loads(open('game.json', encoding='utf-8').read())
    game = games[gameid]
    if dest is None:
        dest = basename + ".png"
    else:
        if os.path.isdir(dest):
            raise ValueError('输出必须是文件')

    infoDic = rep.getBaseInfoDic()

    class Strings:
        title = '东方Project战报'
        basic_info = '基本信息'
        score_info = '得分信息'
        name = '玩家'
        date = '时间'
        character = '机体'
        rank = '难度'
        stage = '进行度'
        slow_rate = '处理落率'

    class Palette:
        def __init__(self, color):
            self.primary = color

    title_font = ImageFont.truetype('simhei.ttf', 36)
    info_font = ImageFont.truetype('simhei.ttf', 24)
    small_font = ImageFont.truetype('simhei.ttf', 16)
    img = Image.new('RGBA', (width, height), '#ffffff')
    draw = ImageDraw.Draw(img)

    colors = json.loads(open('color.json').read())
    palette = Palette(colors[gameid]['primary'])

    def drawInfo(x, y, text, color=palette.primary):
        sizex, sizey = info_font.getsize(text)
        draw.text((x, y-sizey/2), text, color, info_font)

    def drawValue(x, y, text):
        sizex, sizey = info_font.getsize(text)
        draw.text((x-sizex, y-sizey/2), text, "#000000", info_font)

    # 标题
    sizex, sizey = title_font.getsize(Strings.title)

    draw.rectangle((0, 0, width, 64), fill=palette.primary)
    draw.text((240-sizex/2, 32-sizey/2), Strings.title, "#ffffff", title_font)

    # 游戏名称
    sizex, sizey = small_font.getsize(game)

    draw.rectangle((0, 72, width, 96), fill=palette.primary)
    draw.text((240-sizex/2, 84-sizey/2), game, "#ffffff", small_font)

    # 基本信息

    drawInfo(20, 120, Strings.basic_info)
    draw.rectangle((20, 138, width-20, 140), fill=palette.primary)

    drawInfo(40, 160, Strings.name)
    drawValue(width-40, 160, rep.getPlayer())
    drawInfo(40, 192, Strings.date)
    drawValue(width-40, 192, rep.getDate())
    drawInfo(40, 224, Strings.character)
    drawValue(width-40, 224,
              "{0} {1}".format(infoDic['character'], infoDic['shottype']))
    drawInfo(40, 256, Strings.rank)
    drawValue(width-40, 256, infoDic['rank'])
    drawInfo(40, 288, Strings.stage)
    drawValue(width-40, 288, infoDic['stage'])
    drawInfo(40, 320, Strings.slow_rate)
    drawValue(width-40, 320, "{:.2f} %".format(rep.getSlowRate()))

    # 得分信息
    drawInfo(20, 360, Strings.score_info)
    draw.rectangle((20, 378, width-20, 380), fill=palette.primary)

    scores = rep.getStageScore()
    for i in range(len(scores)):
        drawInfo(40, i*32+400, "Stage {0}".format(i+1))
        drawValue(width-40, i*32+400, "{:,d}".format(scores[i]))

    draw.rectangle((0, height, width, height-20), fill=palette.primary)

    digest = hashlib.md5(open(rpy, 'rb').read()).hexdigest()
    sizex, sizey = small_font.getsize(digest)
    draw.text((240-sizex/2, 630-sizey/2), digest, "#ffffff", small_font)

    # 保存
    img.save(dest, 'png')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str,
                        help='输出文件')
    parser.add_argument('file', type=str,
                        help='输入文件')
    args = parser.parse_args()
    generateImage(args.file, args.output)
