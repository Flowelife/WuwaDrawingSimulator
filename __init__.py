import random
import json
import os
import time
from PIL import Image, ImageDraw, ImageFont
from math import sin, ceil, pi
from typing import Iterator

class SimulatorConfig:
    """模拟器参数配置"""
    default_prize_pool = '挽歌永不落幕'  # 默认卡池
    maximum_draw_5 = 80                 # 5星保底次数
    maximum_draw_4 = 10                 # 4星保底次数
    basic_probability_5 = 0.8 / 100     # 5星基础概率
    basic_probability_4 = 6 / 100       # 4星基础概率
    charactor_upper_probability = False # 5星角色是否是不歪池
    arms_upper_probability = True       # 5星武器是否是不歪池
    # 图像文字字体
    image_font_path = os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'SmileySans-Oblique.ttf')
    image_star_font_size = 40   # 星级字体大小
    image_name_font_size = 30   # 名称字体大小
    image_background = (31,31,31,255)  # 图片大背景

class PrizePool:
    """卡池类，提供卡池信息和验证功能。"""

    __prize_info = json.loads(
        open(os.path.join(os.path.dirname(__file__), 'prize_info.json'), 'r', encoding='utf-8').read()
    )
    """__prize_info: dict
        - all_prizes: dict
            - 3: list 3星武器
            - 4: dict
                - arms: list 4星武器
                - characters: list 4星角色
            - 5: dict
                - up: str 5星武器或角色
                - normal: list 5星武器或角色
        - version: dict
            - 版本号: list 卡池信息
        - prize_pool: dict
            - 卡池名: dict
                - type: str 卡池类型 ('character' 或 'arms')
                - 4: list 4星up角色或武器
                - 5: str 5星up角色或武器
    """
    __characters_name = json.loads(
        open(os.path.join(os.path.dirname(__file__), 'character_name.json'), 'r', encoding='utf-8').read() 
    ) 
    """__characters_name: dict
        - 角色名: str 角色中文名"""

    @classmethod
    def get_version_prize_pool(cls, version: str = '2.4') -> list:
        """获取指定版本的卡池信息。
        
        RETURN:
        - list: 返回指定版本的卡池信息列表。"""
        if version not in cls.__prize_info['version']:
            raise ValueError(f"Version {version} not found in prize info.")
        return cls.__prize_info['version'][version]
    
    @classmethod
    def get_prize_pool_info(cls, prize_pool: str = SimulatorConfig.default_prize_pool) -> dict:
        """获取指定卡池的up信息。
        
        RETURN:
        - dict: 返回指定卡池的up信息字典，包含type、4和5星up信息。
            - type: str 卡池类型 ('character' 或 'arms')
            - 4: list 4星up角色或武器
            - 5: str 5星up角色或武器"""
        if prize_pool not in cls.__prize_info['prize_pool']:
            raise ValueError(f"Prize pool {prize_pool} not found in prize info.")
        return cls.__prize_info['prize_pool'][prize_pool]
    
    @classmethod
    def get_prize_pool_list(cls) -> list:
        """获取所有可用的卡池列表。
        
        RETURN:
        - list: 返回所有可用的卡池名称列表。"""
        return list(cls.__prize_info['prize_pool'].keys())
    
    @classmethod
    def get_last_prize_pool(cls) -> str:
        """获取最新版本的一个卡池名称

        RETURN:
        - str: 卡池名称
        """
        version = list(cls.__prize_info['version'].keys())
        version = sorted(version, key=lambda x: float(x), reverse=True)
        return cls.__prize_info['version'][version[0]][0]

    @classmethod
    def prize_pool_generate(cls, prize_pool: str = SimulatorConfig.default_prize_pool) -> dict:
        """生成指定卡池内容字典。
        
        RETURN:
        - dict: 返回指定卡池的内容字典，包含type、3、4和5星up信息。
            - type: str 卡池类型 ('character' 或 'arms')
            - 3: list 3星武器
            - 4: dict
                - up: list 4星up角色或武器
                - normal: list 4星普通角色或武器
            - 5: dict
                - up: str 5星up角色或武器
                - normal: list 5星普通角色或武器"""
        prize_info = cls.get_prize_pool_info(prize_pool)
        result = {
            'type': prize_info['type'],
            '3': cls.__prize_info['all_prizes']['3'],
            '4': {
                'up': prize_info['4'],
                'normal': cls.__prize_info['all_prizes']['4']['arms'] + \
                        [item for item in cls.__prize_info['all_prizes']['4']['characters'] if item not in prize_info['4']]\
                        \
                        if prize_info['type'] == 'character' else\
                        \
                        [item for item in cls.__prize_info['all_prizes']['4']['arms'] if item not in prize_info['4']]
            },
            '5': {
                'up': prize_info['5'],
                'normal': ['CALCHARO','JIANXIN','VERINA', 'LINGYANG', 'ENCORE']
            }
        }
        return result
    
    @classmethod
    def check_prize_pool(cls, prize_pool: dict) -> tuple[bool, str]:
        """检查卡池内容是否符合规范。"""
        if 'type' not in prize_pool or prize_pool['type'] not in ['character', 'arms']:
            return False, "Invalid prize pool type."
        if '3' not in prize_pool or not isinstance(prize_pool['3'], list):
            return False, "Invalid or missing 3-star prizes."
        if '4' not in prize_pool or not isinstance(prize_pool['4'], dict):
            return False, "Invalid or missing 4-star prizes."
        if 'up' not in prize_pool['4'] or not isinstance(prize_pool['4']['up'], list):
            return False, "Invalid or missing 4-star up prizes."
        if len(prize_pool['4']['up']) != 3:
            return False, "4-star up prizes must contain exactly 3 items."
        if 'normal' not in prize_pool['4'] or not isinstance(prize_pool['4']['normal'], list):
            return False, "Invalid or missing 4-star normal prizes."
        if '5' not in prize_pool or not isinstance(prize_pool['5'], dict):
            return False, "Invalid or missing 5-star prizes."
        if 'up' not in prize_pool['5'] or not isinstance(prize_pool['5']['up'], str):
            return False, "Invalid or missing 5-star up prize."
        if prize_pool['type'] == 'character' and 'normal' not in prize_pool['5']:
            return False, "Missing 5-star normal prizes for character type."
        return True, "Prize pool is valid."
    
    @classmethod
    def get_character_name(cls, character: str) -> str:
        """获取角色的中文名。"""
        if character not in cls.__characters_name:
            raise ValueError(f"Character {character} not found in character names.")
        return cls.__characters_name[character]
    
    @classmethod
    def get_all_characters_name(cls) -> dict:
        return cls.__characters_name


class Reward:
    """奖励类，封装了抽卡结果和相关统计信息。"""
    def __init__(self, rewards: list, prize_pool: str, draw_time: time.struct_time = time.localtime()) -> None:
        self.__rewards = rewards
        self.__prize_pool = prize_pool
        self.__time = time.strftime("%Y-%m-%d %H:%M:%S", draw_time)
        self.__len = len(rewards)
        self.count_3_star = sum(1 for item in rewards if item[1] == 3)
        self.count_4_star = sum(1 for item in rewards if item[1] == 4)
        self.count_5_star = sum(1 for item in rewards if item[1] == 5)

    def __len__(self) -> int:
        return self.__len

    def __repr__(self) -> str:
        return f"Reward(3-star: {self.count_3_star}, 4-star: {self.count_4_star}, 5-star: {self.count_5_star}, rewards: {self.__rewards}, time: {self.__time}, prize_pool: {self.__prize_pool})"
    
    def __format__(self, format_spec: str) -> str:
        result = f'{self.__prize_pool}\n'
        for item in self.__rewards:
            result += f"{item[0]}, {item[1]}-star, {self.__time}\n"
        return result
    
    def __iter__(self) -> Iterator:
        return iter(self.__rewards)
    
    def __add__(self, other: 'Reward') -> 'Reward':
        if not isinstance(other, Reward):
            raise TypeError("Can only add Reward instances.")
        if self.__prize_pool != other.prize_pool:
            raise ValueError("Only rewards with the same prize pool can be added.")
        return Reward(self.__rewards + other.__rewards, self.__prize_pool)
    
    @property
    def prize_pool(self) -> str: 
        """卡池名称"""
        return self.__prize_pool

    @property
    def rewards(self) -> list:
        """所有奖励。"""
        return self.__rewards

    @property
    def count(self) -> dict:
        """各星级奖励的数量。"""
        return {
            '3': self.count_3_star,
            '4': self.count_4_star,
            '5': self.count_5_star
        }

    def sort(self, reverse: bool = False) -> 'Reward':
        """对奖励列表进行排序。
        
        PARAMS:
        - reverse: bool 是否反向排序，默认为False。"""
        self.__rewards.sort(key=lambda x: x[1], reverse=reverse)
        return self

    def get_3_rewards(self) -> list:
        """返回所有3星奖励。
        
        RETURN:
        - list: 包含所有3星奖励名称的列表。"""
        return [item[0] for item in self.__rewards if item[1] == 3]
    
    def get_4_rewards(self) -> list:
        """返回所有4星奖励。
        
        RETURN:
        - list: 包含所有4星奖励名称的列表。"""
        return [item[0] for item in self.__rewards if item[1] == 4]
    
    def get_5_rewards(self) -> list:
        """返回所有5星奖励。

        RETURN:
        - list: 包含所有5星奖励名称的列表。"""
        return [item[0] for item in self.__rewards if item[1] == 5]
    
    def split(self, x: int = 10) -> list['Reward']:
        """按x一组进行分割
        
        PARAMS:
        - x: int 每组元素个数
        
        RETURN:
        - list[Reward]: 分组后列表"""
        if x <= 0:
            raise ValueError("x cannot be less than 0.")
        if x >= self.__len:
            return [Reward(self.__rewards, self.__prize_pool)]
        result = []
        for i in range(x, self.__len+x, x):
            result.append(Reward(self.__rewards[i-x:i], self.__prize_pool))
        return result
    
    def to_image(self) -> Image.Image:
        """将奖励转换为图像。

        RETURN:
        - Image: 返回包含奖励的图像。"""
        padding = 2         # 间距
        item_width = 256    # 每个物品的宽度
        icon_item_height = 253 # 每个物品图标的高度

        item_count_x = 10 if self.__len >= 10 else self.__len
        item_count_y = 1 if self.__len <= 10 else ceil(self.__len/10)
        
        image_width = item_width * item_count_x + padding * (item_count_x + 1) # x轴上物品的宽度加上间距
        image_width = 1920 if image_width <= 1920 else image_width

        if self.__len <= 10:
            # 奖品排序
            rewards = self.sort(reverse=True)
            # 图像高度计算
            image_height = int(image_width * 0.5625) # 图像高度
            image_height = 1080 if image_height <= 1080 else image_height
            item_height = image_height  # 物品高度
        else:
            # 奖品排序
            rewards = Reward([], self.__prize_pool)
            temp = self.split(10)
            for item in temp:
                item.sort(reverse=True)
                rewards += item
            # 图像高度计算
            item_height = icon_item_height + SimulatorConfig.image_star_font_size + SimulatorConfig.image_name_font_size
            image_height = item_height * item_count_y + padding * (item_count_x + 1)

        front_image = Image.new('RGBA', (image_width, image_height), SimulatorConfig.image_background) # 展示盒
        image_draw = ImageDraw.Draw(front_image)  # 展示盒绘制对象
        star_font = ImageFont.truetype(SimulatorConfig.image_font_path, SimulatorConfig.image_star_font_size) # 星级字体
        name_font = ImageFont.truetype(SimulatorConfig.image_font_path, SimulatorConfig.image_name_font_size) # 名称字体
        color_5_star = (255,233,108)    # 5星颜色
        color_4_star = (201,131,237)    # 4星颜色
        color_3_star = (117,187,231)    # 3星颜色
        # 绘制物品
        index = 0
        for item in rewards.rewards:
            name, star = item
            background_color = color_5_star if star == 5 else (color_4_star if star == 4 else color_3_star) # 物品背景颜色
            # 创建背景渐变
            background = Image.new('RGBA', (item_width, item_height), SimulatorConfig.image_background)
            background_draw = ImageDraw.Draw(background)
            for i in range(0, item_height):
                # 计算渐变因子
                x = (i / item_height)*2*pi
                factor = sin(x/2) if self.__len <= 10 else sin(x/4)
                # 计算渐变颜色   
                gradient_color = (
                    int((background_color[0]-80) * factor if factor > 0 else 0),
                    int((background_color[1]-80) * factor if factor > 0 else 0),
                    int((background_color[2]-80) * factor if factor > 0 else 0),
                    int(255 * factor - 5 if factor > 0 else 0)
                )
                # 绘制渐变线条
                background_draw.line([(0, i), (item_width, i)], fill=gradient_color)
            item_image = Image.open(os.path.join(os.path.dirname(__file__), 'resources', f'{star}', f'{name}.png')).convert('RGBA')
            x = (index % 10) * item_width + padding * (index % 10 + 1)
            y = (index // 10) * item_height + padding * (index // 10 + 1)
            item_image = item_image.resize((item_width, icon_item_height), Image.Resampling.LANCZOS)   # 调整物品大小
            # 绘制物品背景和名称
            front_image.paste(background, (x, y), background)
            front_image.paste(item_image, (x, y+(item_height//2 - icon_item_height//2)), item_image)
            x = x
            y = y + (item_height//2 + icon_item_height//4) + SimulatorConfig.image_star_font_size
            image_draw.text((x, y), f"{'★'*star}", fill=background_color, font=star_font)
            if name in PrizePool.get_all_characters_name(): name = PrizePool.get_character_name(name)
            image_draw.text((x, y + SimulatorConfig.image_star_font_size), f"{name}", fill=(255, 255, 255), font=name_font)
            index += 1
        if self.__len <= 10:
            result = Image.open(os.path.join(os.path.dirname(__file__), 'resources', 'background', f'{self.prize_pool}.jpg')).convert('RGBA').resize(front_image.size)
            result.paste(front_image,(0,0),front_image)
        else:
            cover = Image.open(os.path.join(os.path.dirname(__file__), 'resources', 'background', f'{self.prize_pool}.jpg')).convert('RGBA').resize((image_width, int(image_width * 0.5625)))
            result = Image.new('RGBA',(image_width, image_height + cover.size[1]), SimulatorConfig.image_background)
            result.paste(cover,(0,0))
            result.paste(front_image,(0,cover.size[1]),front_image)
        return result


class Simulator:
    """抽卡模拟器类，提供抽卡功能和保底机制。"""
    def __init__(self, prize_pool: str = SimulatorConfig.default_prize_pool, inherit_guaranteed_counts_5: int =0, inherit_guaranteed_counts_4: int =0, upper_promise_5: bool = False, upper_promise_4: bool = False) -> None:
        """初始化抽卡模拟器。
        
        TIPS: prize_pool参数必须是通过PrizePool.prize_pool_generate()方法生成的字典。"""
        prize_pool_data = PrizePool.prize_pool_generate(prize_pool)
        check = PrizePool.check_prize_pool(prize_pool_data)
        if check[0] is False:
            raise ValueError(check[1])
        self.__maximum_draw_5 = SimulatorConfig.maximum_draw_5
        self.__maximum_draw_4 = SimulatorConfig.maximum_draw_4
        self.__basic_probability_5 = SimulatorConfig.basic_probability_5
        self.__basic_probability_4 = SimulatorConfig.basic_probability_4
        self.__prize_pool = prize_pool
        self.__prize_pool_data = prize_pool_data   # 卡池内容字典 通过 PrizePool.prize_pool_generate() 获取
        self.__guaranteed_counts_5 = inherit_guaranteed_counts_5 if inherit_guaranteed_counts_5 >= 0 else 0# 5星已抽取次数
        self.__guaranteed_counts_4 = inherit_guaranteed_counts_4 if inherit_guaranteed_counts_4 >= 0 else 0# 4星已抽取次数
        self.__upper_probability =  SimulatorConfig.charactor_upper_probability \
                                    if prize_pool_data['type'] == 'character' else \
                                    SimulatorConfig.arms_upper_probability # 是否启用5星不歪池
        self.__upper_promise_5 = upper_promise_5     # 下一个5星是否必出up
        self.__upper_promise_4 = upper_promise_4    # 下一个4星是否必出up

    @property
    def prize_pool(self) -> str: return self.prize_pool

    @property
    def guaranteed_counts_5(self) -> int: return self.__guaranteed_counts_5

    @property
    def guaranteed_counts_4(self) -> int: return self.__guaranteed_counts_4

    @property
    def upper_probability(self) -> int: return self.__upper_probability

    @property
    def upper_promise_5(self) -> bool: return self.__upper_promise_5

    @property
    def upper_promise_4(self) -> bool: return self.__upper_promise_4

    def draw(self, counts: int=10) -> Reward:
        """模拟抽卡。
        
        PARAMS:
        - counts: int 抽卡次数，默认为10次。
        
        RETURN:
        - Reward: 返回抽卡结果的 Reward 对象。"""
        if counts < 1:
            return Reward([], self.__prize_pool)
        result = []
        for _ in range(counts):
            dice_roll = random.random()
            self.__guaranteed_counts_5 += 1
            if self.__guaranteed_counts_5 >= self.__maximum_draw_5 or dice_roll < self.__basic_probability_5:
                if self.__upper_promise_5 or self.__upper_probability or random.choice([True, False]):
                    result.append((self.__prize_pool_data['5']['up'], 5))
                    self.__upper_promise_5 = False
                else:
                    result.append((random.choice((self.__prize_pool_data['5']['normal'])), 5))
                    self.__upper_promise_5 = True
                self.__guaranteed_counts_5 = 0
                continue
            self.__guaranteed_counts_4 += 1
            if self.__guaranteed_counts_4 >= self.__maximum_draw_4 or dice_roll < self.__basic_probability_4:
                if self.__upper_promise_4 or random.choice([True, False]):
                    result.append((random.choice(self.__prize_pool_data['4']['up']), 4))
                    self.__upper_promise_4 = False
                else:
                    result.append((random.choice(self.__prize_pool_data['4']['normal']), 4))
                    self.__upper_promise_4 = True
                self.__guaranteed_counts_4 = 0
                continue
            result.append((random.choice(self.__prize_pool_data['3']), 3))
        return Reward(result, self.__prize_pool)