import random
import json
import os
import time
from PIL import Image, ImageDraw, ImageFont
from math import sin, pi
from typing import Iterator

class PrizePool:
    """
    卡池类，提供卡池信息和验证功能。"""

    _prize_info = json.loads(
        open(os.path.join(os.path.dirname(__file__), 'prize_info.json'), 'r', encoding='utf-8').read()
    )
    """_prize_info: dict
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
    _characters_name = json.loads(
        open(os.path.join(os.path.dirname(__file__), 'character_name.json'), 'r', encoding='utf-8').read() 
    ) 
    """_characters_name: dict
        - 角色名: str 角色中文名"""

    @classmethod
    def get_version_prize_pool(cls, version: str = '2.4') -> list:
        """获取指定版本的卡池信息。
        
        RETURN:
        - list: 返回指定版本的卡池信息列表。"""
        if version not in cls._prize_info['version']:
            raise ValueError(f"Version {version} not found in prize info.")
        return cls._prize_info['version'][version]
    
    @classmethod
    def get_prize_pool_info(cls, prize_pool: str = '胜利为我喝彩') -> dict:
        """获取指定卡池的up信息。
        
        RETURN:
        - dict: 返回指定卡池的up信息字典，包含type、4和5星up信息。
            - type: str 卡池类型 ('character' 或 'arms')
            - 4: list 4星up角色或武器
            - 5: str 5星up角色或武器"""
        if prize_pool not in cls._prize_info['prize_pool']:
            raise ValueError(f"Prize pool {prize_pool} not found in prize info.")
        return cls._prize_info['prize_pool'][prize_pool]
    
    @classmethod
    def get_prize_pool_list(cls) -> list:
        """获取所有可用的卡池列表。
        
        RETURN:
        - list: 返回所有可用的卡池名称列表。"""
        return list(cls._prize_info['prize_pool'].keys())
    
    @classmethod
    def prize_pool_generate(cls, prize_pool: str = '胜利为我喝彩') -> dict:
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
            '3': cls._prize_info['all_prizes']['3'],
            '4': {
                'up': prize_info['4'],
                'normal': cls._prize_info['all_prizes']['4']['arms'] + \
                        [item for item in cls._prize_info['all_prizes']['4']['characters'] if item not in prize_info['4']]\
                        \
                        if prize_info['type'] == 'character' else\
                        \
                        [item for item in cls._prize_info['all_prizes']['4']['arms'] if item not in prize_info['4']]
            },
            '5': {
                'up': prize_info['5'],
                'normal': ['CALCHARO','JIANXIN','VERINA', 'LINGYANG', 'ENCORE'] if prize_info['type'] == 'character' else None
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
        if character not in cls._characters_name:
            raise ValueError(f"Character {character} not found in character names.")
        return cls._characters_name[character]

class Reward:
    """奖励类，封装了抽卡结果和相关统计信息。"""
    def __init__(self, rewards: list, time: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) -> None:
        self._rewards = rewards
        self._time = time
        self._len = len(rewards)
        self._3_count = sum(1 for item in rewards if item[1] == 3)
        self._4_count = sum(1 for item in rewards if item[1] == 4)
        self._5_count = sum(1 for item in rewards if item[1] == 5)

    def __len__(self) -> int:
        """返回奖励列表的长度。"""
        return self._len

    def __repr__(self) -> str:
        return f"Reward(3-star: {self._3_count}, 4-star: {self._4_count}, 5-star: {self._5_count}, rewards: {self._rewards})"
    
    def __format__(self, format_spec: str) -> str:
        result = ''
        for item in self._rewards:
            result += f"{item[0]}, {item[1]}-star, {self._time}\n"
        return result
    
    def __iter__(self) -> Iterator:
        return iter(self._rewards)
    
    def __add__(self, other: 'Reward') -> 'Reward':
        if not isinstance(other, Reward):
            raise TypeError("Can only add Reward instances.")
        return Reward(self._rewards + other._rewards)

    @property
    def rewards(self) -> list:
        """返回所有奖励。"""
        return self._rewards

    @property
    def count(self) -> dict:
        """返回各星级奖励的数量。

        RETURN:
        - dict: 包含3星、4星和5星奖励数量的字典。
        """
        return {
            '3': self._3_count,
            '4': self._4_count,
            '5': self._5_count
        }
    
    def sort(self, reverse: bool = False) -> None:
        """对奖励列表进行排序。
        
        PARAMS:
        - reverse: bool 是否反向排序，默认为False。"""
        self._rewards.sort(key=lambda x: x[1], reverse=reverse)

    def get_3_rewards(self) -> list:
        """返回所有3星奖励。
        
        RETURN:
        - list: 包含所有3星奖励名称的列表。"""
        return [item[0] for item in self._rewards if item[1] == 3]
    
    def get_4_rewards(self) -> list:
        """返回所有4星奖励。
        
        RETURN:
        - list: 包含所有4星奖励名称的列表。"""
        return [item[0] for item in self._rewards if item[1] == 4]
    
    def get_5_rewards(self) -> list:
        """返回所有5星奖励。

        RETURN:
        - list: 包含所有5星奖励名称的列表。"""
        return [item[0] for item in self._rewards if item[1] == 5]
    
    def to_image(self) -> Image.Image:
        """将奖励转换为图像。

        RETURN:
        - Image: 返回包含奖励的图像。"""
        if self._len != 10:
            raise ValueError("Reward list must contain exactly 10 items for image generation.")
        self.sort(reverse=True)  # 按星级降序排序
        padding = 2         # 间距
        item_width = 256    # 每个物品的宽度
        transform_item_height = 253 # 每个物品的高度
        image_width = item_width * 10 + padding * 11 # 10个物品的宽度加上间距
        image_height = 720 # 图像高度
        image = Image.new('RGB', (image_width, image_height), (0,0,0)) # 底图
        image_draw = ImageDraw.Draw(image)  # 底图绘制对象
        star_font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'SmileySans-Oblique.ttf'), 35) # 星级字体
        name_font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'SmileySans-Oblique.ttf'), 30) # 名称字体
        color_5_star = (255,233,108)    # 5星颜色
        color_4_star = (201,131,237)    # 4星颜色
        color_3_star = (117,187,231)    # 3星颜色
        # 绘制物品
        index = 0
        for item in self._rewards:
            name, star = item
            background_color = color_5_star if star == 5 else (color_4_star if star == 4 else color_3_star) # 物品背景颜色
            # 创建背景渐变
            background = Image.new('RGB', (item_width, image_height), (0,0,0))
            background_draw = ImageDraw.Draw(background)
            for i in range(0, image_height):
                # 计算渐变因子
                x = (i / image_height)*2*pi
                factor = sin(x/2)
                # 计算渐变颜色   
                gradient_color = (
                    int((background_color[0]-20) * factor if factor > 0 else 0),
                    int((background_color[1]-20) * factor if factor > 0 else 0),
                    int((background_color[2]-20) * factor if factor > 0 else 0)
                )
                # 绘制渐变线条
                background_draw.line([(0, i), (item_width, i)], fill=gradient_color)
            item_image = Image.open(os.path.join(os.path.dirname(__file__), 'resources', f'{star}', f'{name}.png'))
            x = (index % 10) * item_width + padding * (index % 10 + 1)
            item_image = item_image.resize((item_width, transform_item_height), Image.Resampling.LANCZOS)   # 调整物品大小
            # 绘制物品背景和名称
            image.paste(background, (x, 0))
            image.paste(item_image, (x, image_height//2 - transform_item_height//2))
            image_draw.text((x + padding, image_height - transform_item_height - 25), f"{'★'*star}", fill=background_color, font=star_font)
            if name in PrizePool._characters_name:
                name = PrizePool.get_character_name(name)
            image_draw.text((x + padding, image_height - transform_item_height + 10), f"{name}", fill=(255, 255, 255), font=name_font)
            index += 1
        return image


class CardDrawingSimulator:
    """抽卡模拟器类，提供抽卡功能和保底机制。"""
    _5_tatol_counts = 80    # 5星保底次数
    _4_total_counts = 10    # 4星保底次数
    _5_basic_probability = 0.8 / 100    # 5星基础概率
    _4_basic_probability = 6 / 100      # 4星基础概率

    def __init__(self, prize_pool: dict = PrizePool.prize_pool_generate(), inherit_5_guaranteed_counts: int =0, inherit_4_guaranteed_counts: int =0, _5_upper_promise: bool = False, _4_upper_promise: bool = False) -> None:
        """初始化抽卡模拟器。
        
        TIPS: prize_pool参数必须是通过PrizePool.prize_pool_generate()方法生成的字典。"""
        if PrizePool.check_prize_pool(prize_pool)[0] is False:
            raise ValueError(PrizePool.check_prize_pool(prize_pool)[1])
        self._prize_pool = prize_pool   # 卡池内容字典 通过 PrizePool.prize_pool_generate() 获取
        self._5_guaranteed_counts = inherit_5_guaranteed_counts # 5星已抽取次数
        self._4_guaranteed_counts = inherit_4_guaranteed_counts # 4星已抽取次数
        self._upper_probability = False  if prize_pool['type'] == 'character' else True # 是否启用5星不歪池
        self._5_upper_promise =_5_upper_promise     # 下一个5星是否必出up
        self._4_upper_promise = _4_upper_promise    # 下一个4星是否必出up

    def draw(self, counts=10) -> Reward:
        """模拟抽卡。
        
        PARAMS:
        - counts: int 抽卡次数，默认为10次。
        
        RETURN:
        - Reward: 返回抽卡结果的 Reward 对象。"""
        result = []
        for _ in range(counts):
            dice_roll = random.random()
            self._5_guaranteed_counts += 1
            if self._5_guaranteed_counts >= self._5_tatol_counts or dice_roll < self._5_basic_probability:
                if self._5_upper_promise or self._upper_probability or random.choice([True, False]):
                    result.append((self._prize_pool['5']['up'], 5))
                    self._5_upper_promise = False
                else:
                    result.append((random.choice((self._prize_pool['5']['normal'])), 5))
                    self._5_upper_promise = True
                self._5_guaranteed_counts = 0
                continue
            self._4_guaranteed_counts += 1
            if self._4_guaranteed_counts >= self._4_total_counts or dice_roll < self._4_basic_probability:
                if self._4_upper_promise or random.choice([True, False]):
                    result.append((random.choice(self._prize_pool['4']['up']), 4))
                    self._4_upper_promise = False
                else:
                    result.append((random.choice(self._prize_pool['4']['normal']), 4))
                    self._4_upper_promise = True
                self._4_guaranteed_counts = 0
                continue
            result.append((random.choice(self._prize_pool['3']), 3))
        return Reward(result)