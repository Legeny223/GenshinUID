import re,os,random,sqlite3,sys,datetime,math,json,time
import base64,traceback
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from shutil import copyfile
import urllib.parse
import httpx

from getInfo.getDB import (connectDB, cookiesDB, deletecache, selectDB, get_alots, cacheDB, errorDB, change_guild, check_switch,record,change_switch,check_subGuild_switch,change_subGuild_switch,subGuild_status)
from getInfo.getData import (GetInfo,GetWeaponInfo,GetCharInfo,GetUidPic,GetMysInfo,GetAudioInfo)
from getInfo.getMes import (foods_wiki, artifacts_wiki, enemies_wiki, sign, daily, weapon_wiki, char_wiki, audio_wiki, award, deal_ck)
from getInfo.getImg import (draw_event_pic)

import yaml
import asyncio
import qqbot
from qqbot.model.guild import Guild
from qqbot.model.audio import AudioControl
from qqbot.model.message import (
    MessageSendRequest,
    MessageArk,
    Message,
    CreateDirectMessageRequest,
    DirectMessageGuild,
)
from qqbot.core.util import logging
from qqbot.model.user import ReqOption

logger = logging.getLogger(__name__)

with open('Config.yaml', encoding='UTF-8') as yaml_file:
    token = yaml.safe_load(yaml_file)

token = qqbot.Token(token["BotID"],token["BotToken"])

api = qqbot.AsyncUserAPI(token, False)
guild_api = qqbot.AsyncGuildAPI(token,False)
audio_api = qqbot.AsyncAudioAPI(token,False)
msg_api = qqbot.AsyncMessageAPI(token, False)
guild_member_api = qqbot.AsyncGuildMemberAPI(token,False)
channel_api = qqbot.AsyncChannelAPI(token,False)

async def up_guild_list():
    guild_list = []
    guild_list_temp = []

    while(1):
        if guild_list != [] and len(guild_list_temp) >= 100:
            guild_list_temp = await api.me_guilds(option = ReqOption(after = str(guild_list_temp[-1].id)))
            guild_list += guild_list_temp
        elif guild_list == []:
            guild_list = await api.me_guilds()
            guild_list_temp = guild_list
        else:
            break

    for guild in guild_list:
        await change_guild("new",guild.id,guild.name)

async def new_guild(guild:Guild):
    await change_guild("new",guild.id,guild.name)

async def delete_guild(guild):
    await change_guild("delete",guild.id,guild.name)

async def ready():
    user = await api.me()
    await up_guild_list()
    print(user.username)

loop = asyncio.get_event_loop()
loop.run_until_complete(ready())

scheduler = AsyncIOScheduler()
scheduler.add_job(deletecache, 'cron', hour='0')
scheduler.start()

audio_raw_ark = {
    "template_id": 24,
    "kv": [
      {
        "key": "#DESC#",
        "value": ""
      },
      {
        "key": "#PROMPT#",
        "value": ""
      },
      {
        "key": "#TITLE#",
        "value": ""
      },
      {
        "key": "#METADESC#",
        "value": ""
      },
      {
        "key": "#IMG#",
        "value": ""
      },
      {
        "key": "#LINK#",
        "value": ""
      },
      {
        "key": "#SUBTITLE#",
        "value": ""
      }
    ]
}

help_ark = MessageArk(data = {
    "template_id": 23,
    "kv": [
      {
        "key": "#DESC#",
        "value": "原神Bot-奶香的一刀"
      },
      {
        "key": "#PROMPT#",
        "value": "这是一份原神Bot帮助"
      },
      {
        "key": "#LIST#",
        "obj": [
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "======原神Bot======"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "uid+<uid> · 输入9位的原神UID"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "攻略+<角色名字> · 查看角色攻略"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "信息+<角色名字> · 查看角色简介"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "信息+<武器名>字 · 查看武器简介"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "角色+<角色名字> · 查看角色详情"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "武器+<武器名字> · 查看武器详情"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "命座+<1-6>+<角色名字> · 查看命座描述"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "食物+<食物名字> · 查看食物描述"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "天赋+<角色名字>+<1-7> · 查询天赋信息"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "圣遗物+<圣遗物名字> · 套装属性描述"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "原魔+<怪物名字> · 查看怪物信息"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "御神签 · 与游戏内御神签结果无关"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "-------------------"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "需要@机器人使用，+号无需输入"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "<> 表示填入的内容，· 后面为说明"
              }
            ]
          },
        
        ]
      }
    ]
})

master_ark = MessageArk(data = {
    "template_id": 23,
    "kv": [
      {
        "key": "#DESC#",
        "value": "原神Bot-奶香的一刀"
      },
      {
        "key": "#PROMPT#",
        "value": "这是一份原神Bot管理员帮助"
      },
      {
        "key": "#LIST#",
        "obj": [
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "======原神Bot======"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "@机器人+设置频道<开启|关闭>+<#选择子频道>"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "指定Bot使用的子频道"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "可设置多个开启频道，管理Bot使用的频道推荐作为第一个开启的频道，否则设置Bot时会没有响应，设置后仅已开启的频道可用Bot。"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "当设置全部子频道关闭时，默认全局可用"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "======================"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "<开启|关闭>+<功能名字>"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "默认全部功能开启，可关闭指定功能，例如\"关闭uid\"即可关闭uid查询"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "======================"
              }
            ]
          },
          {
            "obj_kv": [
              {
                "key": "desc",
                "value": "如有其他问题可私信小灰灰，或点击机器人头像提交反馈"
              }
            ]
          },
        ]
      }
    ]
})

switch_list = {
    "uid":"SearchRole",
    "mys":"SearchRole",
    "查询":"SearchRole",
    "绑定uid":"LinkUID",
    "绑定mys":"LinkUID",
    "角色":"CharInfo",
    "武器":"WeaponInfo",
    "材料":"CostInfo",
    "天赋":"TalentsInfo",
    "命座":"PolarInfo",
    "攻略":"guideInfo",
    "信息":"CardInfo",
    "御神签":"GetLots",
    "语音":"AudioInfo",
    "食物":"Foods",
    "原魔":"Enemies",
    "圣遗物":"Artifacts",
}

audio_json = {
    "357":["357_01","357_02","357_03"],
    "1000000":["1000000_01","1000000_02","1000000_03","1000000_04","1000000_05","1000000_06","1000000_07"],
    "1000001":["1000001_01","1000001_02","1000001_03"],
    "1000002":["1000002_01","1000002_02","1000002_03"],
    "1000100":["1000100_01","1000100_02","1000100_03","1000100_04","1000100_05"],
    "1000101":["1000101_01","1000101_02","1000101_03","1000101_04","1000101_05","1000101_06"],
    "1000200":["1000200_01","1000200_02","1000200_03"],
    "1010201":["1010201_01"],
    "1000300":["1000300_01","1000300_02"],
    "1000400":["1000400_01","1000400_02","1000400_03"],
    "1000500":["1000500_01","1000500_02","1000500_03"],
    "1010000":["1010000_01","1010000_02","1010000_03","1010000_04","1010000_05"],
    "1010001":["1010001_01","1010001_02"],
    "1010100":["1010100_01","1010100_02","1010100_03","1010100_04","1010100_05"],
    "1010200":["1010200_01","1010200_02","1010200_03","1010200_04","1010200_05"],
    "1010300":["1010300_01","1010300_02","1010300_03","1010300_04","1010300_05"],
    "1010301":["1010301_01","1010301_02","1010301_03","1010301_04","1010301_05"],
    "1010400":["1010400_01","1010400_02","1010400_03"],
    "1020000":["1020000_01"]
}

async def check_cookies():
    with open("cookies_simp.json",'r') as load_f:
        load_dict = json.load(load_f)
    num = 0
    for i in load_dict["data"]:
        aid = re.search(r"account_id=(\d*)", i)
        mysid_data = aid.group(0).split('=')
        mysid = mysid_data[1]
        cookie = ';'.join(filter(lambda x: x.split('=')[0] in [
                          "cookie_token", "account_id"], [j.strip() for j in i.split(';')]))
        uid = int(time.time()) + num
        num += 1
        await cookiesDB(uid, i, 10086)

async def GetUidUrl(uid,qid,nickname,mode = 2):
    try:
        while 1:
            use_cookies = await cacheDB(uid,mode-1)
            if use_cookies == '':
                return "绑定记录不存在。"
            elif use_cookies == "没有可以使用的Cookies！":
                return "没有可以使用的Cookies！"

            if mode == 3:
                mys_data = await GetMysInfo(uid,use_cookies)
                mysid_data = uid
                for i in mys_data['data']['list']:
                    if i['game_id'] != 2:
                        mys_data['data']['list'].remove(i)
                uid = mys_data['data']['list'][0]['game_role_id']
                nickname = mys_data['data']['list'][0]['nickname']
                #role_level = mys_data['data']['list'][0]['level']
                
            raw_data = await GetInfo(uid,use_cookies)
            if raw_data["retcode"] != 0:
                if raw_data["retcode"] == 10001:
                    #return ("Cookie已过期，可联系小灰灰处理！")
                    await errorDB(use_cookies,"error")
                elif raw_data["retcode"] == 10101:
                    #return ("当前查询接口已达到上限，可联系小灰灰处理！")
                    await errorDB(use_cookies,"limit30")
                elif raw_data["retcode"] == 10102:
                    return ("当前查询id已经设置了隐私，无法进行查询！")
                else:
                    return (
                        "Api报错，返回内容为：\r\n"
                        + str(raw_data) + "\r\n出现这种情况可能的UID输入错误 or 不存在"
                    )
            else:
                break
        url = await GetUidPic(raw_data,uid,qid,nickname)
        return url
    except TypeError as e:
        qqbot.logger.info(e.with_traceback)
        return "请求数据为空，可能是绘制图片时出错。"
    except Exception as e:
        qqbot.logger.info(e.with_traceback)
        return "发生错误，频道信息Api可能变动。"

async def getChannelStatus(gid):
    channel_openlist = await subGuild_status(gid)
    mes = "\n当前开启频道："
    if channel_openlist:
        channel_list = await channel_api.get_channels(gid)
        for i in channel_list:
            for j in channel_openlist:
                if i.id == j:
                    mes += "\n<<#{}>>".format(i.id)
    if mes == "\n当前开启频道：":
        mes = "\n当前开启频道：\n可在所有频道使用。"
    return mes

async def _message_handler(event, message: Message):

    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)

    try:
        guild_data = await guild_api.get_guild(message.guild_id)
        at_mes = re.search(r'\<\@\![0-9]+\>',message.content)
        raw_mes = message.content.replace(at_mes.group(),"").replace(" ","").replace("/","")
        record_mes = raw_mes
    except Exception as e:
        qqbot.logger.info(e.with_traceback)
        traceback.print_exc()
        return

    mes = None
    image = None
    ark = None
    audio = None
    
    async def check_startwish(raw_mes,key_word,gid):
        if raw_mes.startswith(key_word) and await check_switch(gid,switch_list[key_word]):
            return True
        else:
            return False

    if raw_mes.startswith("开启"):
        raw_mes = raw_mes.replace("开启","")
        member_info = await guild_member_api.get_guild_member(message.guild_id, message.author.id)
        if "2" in member_info.roles or "4" in member_info.roles or "5" in member_info.roles:
            try:
                await change_switch(message.guild_id,switch_list[raw_mes],"on")
                mes = "成功。"
            except Exception as e:
                traceback.print_exc()
                mes = "发生错误，可能是输入的功能名不正确。"
        else:
            return
    elif raw_mes.startswith("关闭"):
        raw_mes = raw_mes.replace("关闭","")
        member_info = await guild_member_api.get_guild_member(message.guild_id, message.author.id)
        if "2" in member_info.roles or "4" in member_info.roles or "5" in member_info.roles:
            try:
                await change_switch(message.guild_id,switch_list[raw_mes],"off")
                mes = "成功。"
            except Exception as e:
                traceback.print_exc()
                mes = "发生错误，可能是输入的功能名不正确。"
        else:
            return
    elif raw_mes.startswith("设置频道开启"):
        try:
            member_info = await guild_member_api.get_guild_member(message.guild_id, message.author.id)
            if "2" in member_info.roles or "4" in member_info.roles or "5" in member_info.roles:
                channel_name = raw_mes.replace("设置频道开启","").replace("#","")
                channel_list = await channel_api.get_channels(message.guild_id)
                for i in channel_list:
                    temp_name = i.name.replace(" ","")
                    if temp_name == channel_name:
                        channel_id = i.id
                await change_subGuild_switch(message.guild_id,channel_id,"open")
                channel_status = await getChannelStatus(message.guild_id)
                mes = "已设置子频道使用该BOT。\n子频道名称：<<#{}>>\n子频道ID：{}".format(channel_id,channel_id)
                mes += channel_status
            else:
                return
        except Exception as e:
            traceback.print_exc()
            mes = "发生错误，可能是输入的功能名不正确。"
    elif raw_mes.startswith("设置频道关闭"):
        try:
            member_info = await guild_member_api.get_guild_member(message.guild_id, message.author.id)
            if "2" in member_info.roles or "4" in member_info.roles or "5" in member_info.roles:
                channel_name = raw_mes.replace("设置频道关闭","").replace("#","")
                channel_list = await channel_api.get_channels(message.guild_id)
                for i in channel_list:
                    temp_name = i.name.replace(" ","")
                    if temp_name == channel_name:
                        channel_id = i.id
                await change_subGuild_switch(message.guild_id,channel_id,"closed")
                channel_status = await getChannelStatus(message.guild_id)
                mes = "已禁止子频道使用该BOT。\n子频道名称：<<#{}>>\n子频道ID：{}".format(channel_id,channel_id)
                mes += channel_status
            else:
                return
        except Exception as e:
            traceback.print_exc()
            mes = "发生错误，可能是输入的功能名不正确。"


    if not await check_subGuild_switch(message.guild_id,message.channel_id):
        mes = await getChannelStatus(message.guild_id)
    else:
        if raw_mes == "频道信息":
            member_info = await guild_member_api.get_guild_member(message.guild_id, message.author.id)
            if "2" in member_info.roles or "4" in member_info.roles or "5" in member_info.roles:
                try:
                    mes = await getGuildStatus()
                except Exception as e:
                    traceback.print_exc()
                    qqbot.logger.info(e.with_traceback)
                    mes = "发生错误，频道信息Api可能变动。"
            else:
                return
        elif raw_mes == "help":
            ark = help_ark
        elif raw_mes == "master":
            ark = master_ark
        elif raw_mes == "整理cookies":
            try:
                await check_cookies()
                mes = "成功!"
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "ck添加错误。"
        elif await check_startwish(raw_mes,"语音",message.guild_id):
            raw_mes = raw_mes.replace("语音","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                if name == "列表":
                    image = "https://img.genshin.minigg.cn/audio-favicon/audioid.png"
                elif name == "":
                    return
                else:
                    audioid = re.findall(r"[0-9]+", raw_mes)[0]
                    if audioid in audio_json:
                        audioid = random.choice(audio_json[audioid])
                    audio_url = await GetAudioInfo(name,audioid)
                    audio_img = "https://img.genshin.minigg.cn/avatar/{}.png".format(name)
                    audio_str = "{}语音{}".format(name,audioid)
                    audio_raw_ark["kv"][0]["value"] = "角色语音"
                    audio_raw_ark["kv"][1]["value"] = "角色语音"
                    audio_raw_ark["kv"][2]["value"] = audio_str
                    audio_raw_ark["kv"][3]["value"] = "原神角色的语音"
                    audio_raw_ark["kv"][4]["value"] = audio_img
                    audio_raw_ark["kv"][5]["value"] = audio_url
                    audio_raw_ark["kv"][6]["value"] = "原神语音"
                    ark = MessageArk(data = audio_raw_ark)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = e.with_traceback

        elif raw_mes == "查询" and await check_switch(message.guild_id,switch_list["查询"]):
            try:
                uid = await selectDB(message.author.id)
                author = await guild_member_api.get_guild_member(message.guild_id,message.author.id)
                nickname = author.user.username
                get_url = await GetUidUrl(uid[0],message.author.id,nickname,uid[1])
                url = json.loads(get_url)
                if url["url"].startswith("/"):
                    image = "https://yuanshen.minigg.cn" + url["url"]
                    status = urllib.request.urlopen(image).code
                    if status == 200:
                        pass
                    else:
                        image = None
                        mes = "输入格式有误，请检查输入是否为9位国服或者大陆渠道服的UID。\n\n例如：/uid137727130\n\n输入/help查看完整帮助"
                else:
                    mes = image
            except json.JSONDecodeError:
                mes = get_url
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "没有找到绑定信息。"
        elif await check_startwish(raw_mes,"uid",message.guild_id):
            raw_mes = raw_mes.replace("uid","")
            try:
                uid = re.findall(r"[0-9]+", raw_mes)[0]
                if len(uid) != 9:
                    mes = "你输入了错误的uid，请检查输入是否正确。"
                else:
                    get_url = await GetUidUrl(uid,message.author.id,message.author.username)
                    url = json.loads(get_url)
                    if url["url"].startswith("/"):
                        image = "https://yuanshen.minigg.cn" + url["url"]
                        status = urllib.request.urlopen(image).code
                        if status == 200:
                            pass
                        else:
                            image = None
                            mes = "链接不存在，可能由于上游接口查询限制，请稍后重试"
                    else:
                        mes = image
            except json.JSONDecodeError:
                mes = get_url
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "UID输入格式有误，请检查输入是否为9位国服或者大陆渠道服的UID。\n\n例如：/uid137727130\n\n输入/help查看完整帮助"
        elif await check_startwish(raw_mes,"mys",message.guild_id):
            raw_mes = raw_mes.replace("mys","")
            try:
                uid = re.findall(r"[0-9]+", raw_mes)[0]
                get_url = await GetUidUrl(uid,message.author.id,message.author.username,mode=3)
                url = json.loads(get_url)
                if url["url"].startswith("/"):
                    image = "https://yuanshen.minigg.cn" + url["url"]
                    status = urllib.request.urlopen(image).code
                    if status == 200:
                        pass
                    else:
                        image = None
                        mes = "链接不存在，可能由于上游接口查询限制，请稍后重试。"
                else:
                    mes = image
            except json.JSONDecodeError:
                mes = get_url
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "输入格式有误，请检查输入是否为米游社ID。\n\n例如：/mys137727130\n\n输入/help查看完整帮助"
        #elif raw_mes.startswith("活动列表"):
            #draw_event_pic()
        #    pass
        elif await check_startwish(raw_mes,"绑定uid",message.guild_id):
            uid = raw_mes.replace("绑定uid","")
            try:
                await connectDB(userid = message.author.id,uid = uid)
                mes = "绑定uid成功。"
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "绑定失败。"
        elif await check_startwish(raw_mes,"绑定mys",message.guild_id):
            uid = raw_mes.replace("绑定mys","")
            try:
                await connectDB(userid = message.author.id,mys = uid)
                mes = "绑定mysid成功。"
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "绑定失败。"
        elif await check_startwish(raw_mes,"角色",message.guild_id):
            raw_mes = raw_mes.replace("角色","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                level = re.findall(r"[0-9]+", raw_mes)
                if len(level) == 1:
                    mes = await char_wiki(name,"char",level=level[0])
                else:
                    mes = await char_wiki(name)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误，请联系管理员检查后台。"
        elif await check_startwish(raw_mes,"武器",message.guild_id):
            raw_mes = raw_mes.replace("武器","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                level = re.findall(r"[0-9]+", raw_mes)
                if len(level) == 1:
                    mes = await weapon_wiki(name,level=level[0])
                else:
                    mes = await weapon_wiki(name)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误，请联系管理员检查后台。"
        elif await check_startwish(raw_mes,"食物",message.guild_id):
            raw_mes = raw_mes.replace("食物","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                mes = await foods_wiki(name)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误，请联系管理员检查后台。"
        elif await check_startwish(raw_mes,"原魔",message.guild_id):
            raw_mes = raw_mes.replace("原魔","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                mes = await enemies_wiki(name)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误，请联系管理员检查后台。"
        elif await check_startwish(raw_mes,"圣遗物",message.guild_id):
            raw_mes = raw_mes.replace("圣遗物","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                mes = await artifacts_wiki(name)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误，请联系管理员检查后台。"
        elif await check_startwish(raw_mes,"材料",message.guild_id):
            raw_mes = raw_mes.replace("材料","")
            try:
                mes = await char_wiki(raw_mes,"costs")
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "不存在该角色或类型。"
        elif await check_startwish(raw_mes,"天赋",message.guild_id):
            raw_mes = raw_mes.replace("天赋","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                num = re.findall(r"[0-9]+", raw_mes)
                if len(num) == 1:
                    mes = await char_wiki(name,"talents",num[0])
                else:
                    mes = "暂无该天赋数，天赋可查询数量为1~7。\n\n输入/help可查看完整帮助"
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "暂无该角色攻略，请检查角色名字是否正确，需输入完整名字。\n\n输入/help可查看完整帮助"
        elif await check_startwish(raw_mes,"命座",message.guild_id):
            raw_mes = raw_mes.replace("命座","")
            try:
                try:
                    num = int(re.findall(r"\d+", raw_mes)[0])  # str
                except:
                    mes = "参数输入有误。"
                m = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                if num<= 0 or num >6:
                    mes = "暂无该命座数量，命座可查询数量为1-6命。\n\n输入/help可查看完整帮助"
                else:
                    mes = await char_wiki(m, "constellations", num)
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "暂无该角色攻略，请检查角色名字是否正确，需输入完整名字。\n\n输入/help可查看完整帮助"
        elif await check_startwish(raw_mes,"攻略",message.guild_id):
            raw_mes = raw_mes.replace("攻略","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                image = "https://img.genshin.minigg.cn/guide/{}.jpg".format(urllib.parse.quote(name, safe=''))
                status = httpx.get(url = image).text
                if "404 Not Found" in status:
                    image = None
                    mes = "暂无该角色攻略，请检查角色名字是否正确，需输入完整名字。\n\n例如：/攻略申鹤\n\n输入/help可查看完整帮助"
                else:
                    pass
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误。"
        elif await check_startwish(raw_mes,"信息",message.guild_id):
            raw_mes = raw_mes.replace("信息","")
            try:
                name = ''.join(re.findall('[\u4e00-\u9fa5]', raw_mes))
                image = "https://img.genshin.minigg.cn/info/{}.jpg".format(urllib.parse.quote(name, safe=''))
                status = httpx.get(url = image).text
                if "404 Not Found" in status:
                    image = None
                    mes = "暂无该角色攻略，请检查角色名字是否正确，需输入完整名字。\n\n例如：/攻略申鹤\n\n输入/help可查看完整帮助"
                else:
                    pass
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "发生错误。"

        elif raw_mes == "御神签" and await check_switch(message.guild_id,switch_list["御神签"]):
            try:
                raw_data = await get_alots(message.author.id)
                mes = base64.b64decode(raw_data).decode("utf-8")
            except Exception as e:
                traceback.print_exc()
                qqbot.logger.info(e.with_traceback)
                mes = "御神签见底了，稍后再来试试吧！"

    if ark:
        try:
            send = qqbot.MessageSendRequest(content = "",ark = ark, msg_id = message.id)
            await msg_api.post_message(message.channel_id, send)
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,"help")
        except Exception as e:
            try:
                send = qqbot.MessageSendRequest(str(e), message.id)
                await msg_api.post_message(message.channel_id, send)
            except:
                pass
            traceback.print_exc()
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,str(e))
    elif audio:
        try:
            await audio_api.post_audio(channel_id = message.channel_id,audio_control = audio_control)
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,audio)
        except Exception as e:
            try:
                send = qqbot.MessageSendRequest(str(e), message.id)
                await msg_api.post_message(message.channel_id, send)
            except:
                pass
            traceback.print_exc()
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,str(e))
    elif image:
        try:
            send = qqbot.MessageSendRequest(content = "",image = image, msg_id = message.id)
            await msg_api.post_message(message.channel_id, send)
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,image)
        except Exception as e:
            try:
                send = qqbot.MessageSendRequest(str(e), message.id)
                await msg_api.post_message(message.channel_id, send)
            except:
                pass
            traceback.print_exc()
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,str(e))
    elif mes:
        try:
            send = qqbot.MessageSendRequest(mes, message.id)
            await msg_api.post_message(message.channel_id, send)
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,mes)
        except Exception as e:
            try:
                send = qqbot.MessageSendRequest(str(e), message.id)
                await msg_api.post_message(message.channel_id, send)
            except:
                pass
            traceback.print_exc()
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,str(e))
    else:
        mes = "你可能发送了错误的指令或者管理员关闭了该功能，请输入/help查看帮助。"
        try:
            send = qqbot.MessageSendRequest(mes, message.id)
            await msg_api.post_message(message.channel_id, send)
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,mes)
        except Exception as e:
            traceback.print_exc()
            await record(guild_data.name,message.guild_id,message.author.username,message.author.id,record_mes,str(e))
    return

async def _guild_handler(event, guild:Guild):
    print("\n频道已刷新。\n")
    if event == "GUILD_CREATE":
        await new_guild(guild)
    elif event == "GUILD_DELETE":
        await delete_guild(guild)

async def getGuildStatus():

    guild_list = []
    guild_list_temp = []

    while(1):
        if guild_list != [] and len(guild_list_temp) >= 100:
            guild_list_temp = await api.me_guilds(option = ReqOption(after = str(guild_list_temp[-1].id)))
            guild_list += guild_list_temp
        elif guild_list == []:
            guild_list = await api.me_guilds()
            guild_list_temp = guild_list
        else:
            break

    guild_member_all_count = 0
    guild_status_mes  = ""

    for guild in guild_list:
        try:
            guild_data = await guild_api.get_guild(guild.id)
            #guild_status_mes += "【{}】{}人\n".format(guild.name,str(guild_data.member_count))
            guild_member_all_count += guild_data.member_count
        except Exception as e:
            qqbot.logger.info(e.args)
            traceback.print_exc()
    user = await api.me()
    guild_status_mes = "【{}】总加入频道 {} 个,总人数为 {}".format(user.username,str(len(guild_list)),str(guild_member_all_count))
    return guild_status_mes

qqbot_handler2 = qqbot.Handler(qqbot.HandlerType.GUILD_EVENT_HANDLER, _guild_handler)
qqbot_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler)
qqbot.async_listen_events(token, False, qqbot_handler,qqbot_handler2)
