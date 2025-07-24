# 鸣潮抽卡模拟器

## 效果
![GOLD](./docs/gold.png)

## 干啥的
一个简单实现了鸣潮卡池模拟的Python库，包含1.0至今的所有角色/武器卡池。

## 用法
### 安装依赖
请确认您的电脑环境中一包含以下库。
- pillow (PIL)

若未安装请使用 `pip` 进行安装。
```bash
pip install pillow
```

### 使用
将此库克隆到您的项目中并引用。
```bash
git clone https://github.com/Flowelife/WuwaDrawingSimulator.git
```
在您的代码中导入`CardDrawingSimulator`即可快速体验。

```python
from WuwaDrawingSimulator import CardDrawingSimulator

simulator = CardDrawingSimulator()
result = simulator.draw()

print(result)

'''OUTPUT
Reward(3-star: 9, 4-star: 1, 5-star: 0, rewards: [('源能音感仪·测五', 3), ('远行者臂铠·破障', 3), ('暗夜臂铠·夜芒', 3), ('
暗夜长刃·玄明', 3), ('远行者矩阵·探幽', 3), ('远行者佩枪·洞察', 3), ('暗夜佩枪·暗星', 3), ('暗夜矩阵·暝光', 3), ('远行者臂
铠·破障', 3), ('永夜长明', 4)])
'''
```

同一`simulator`进行多次抽取会自动累计保底值。
```python
from WuwaDrawingSimulator import CardDrawingSimulator, Reward

result = Reward([])
simulator = CardDrawingSimulator()
for _ in range(16): # 一个大保底（160抽）
    print(f'5星保底{simulator._5_guaranteed_counts}/80 是否为大保底: {simulator._5_upper_promise}')
    result += simulator.draw()

print(result.count)

'''OUTPUT
5星保底0/80           是否为大保底: False
5星保底10/80           是否为大保底: False
5星保底20/80           是否为大保底: False
5星保底30/80           是否为大保底: False
5星保底40/80           是否为大保底: False
5星保底50/80           是否为大保底: False
5星保底60/80           是否为大保底: False
5星保底70/80           是否为大保底: False
5星保底0/80           是否为大保底: True
5星保底10/80           是否为大保底: True
5星保底20/80           是否为大保底: True
5星保底30/80           是否为大保底: True
5星保底40/80           是否为大保底: True
5星保底50/80           是否为大保底: True
5星保底60/80           是否为大保底: True
5星保底70/80           是否为大保底: True
{'3': 138, '4': 20, '5': 2}
'''
```

`CardDrawingSimulator`初始化参数如下:
|参数名|类型|用途|取值|默认值|
|---|---|---|---|---|
|prize_pool|dict|需要模拟抽取的卡池|由`PrizePool.prize_pool_generate(prize_pool)`生成|`挽歌永不落幕`卡池|
|inherit_5_guaranteed_counts|int|已经多少抽没有出5星了|[0,80]|0|
|inherit_4_guaranteed_counts|int|已经多少抽没有出4星了|[0,10]|0|
|_5_upper_promise|bool|下一个5星是否必定为up|True or False|False|
|_4_upper_promise|bool|下一个4星是否必定为up|True or False|False|

`draw()`返回一个`Reward`对象。

`Reward`中封装了抽取结果，分布统计。您可以使用成员`reward`、`count`来访问它们。

成员`to_image()`函数可以将结果转化为`Image`对象。

__*tip:*__ 该函数仅当`Reward`内只有10个元素时才会生效。
```python
image = result.to_image()
image.show()
```
![result image](./docs/result.PNG)

您可以用这个简单的方式来存储结果。
```python
with open(filename, 'wb') as f: image.save(f)
```

`PrizePool`类用于查询、创建卡池、角色名字转换。
```python
from WuwaDrawingSimulator import PrizePool

pool = PrizePool.get_prize_pool_list()                  # 获取所有卡池名称
pool_by_ver = PrizePool.get_version_prize_pool('2.4')   # 查询游戏某一版本的卡池
info = PrizePool.get_prize_pool_info(pool[0])           # 通过卡池名称查看卡池up信息
prize_pool = PrizePool.prize_pool_generate(pool[0])     # 通过卡池名生成卡池具体内容
name = PrizePool.get_character_name(info['5'])          # 将角色名称转成中文名

print('pool:',pool)
print('\npool_by_ver:', pool_by_ver)
print('\ninfo:', info)
print('\nprize_pool:', prize_pool)
print('\nname:', name)

'''OUTPUT
pool: ['胜利为我喝彩', '焰痕', '却也在风潮后轻舞', '不屈命定之冠', '行于光影之间', '诗与乐的交响', '焰光裁定', '林间的咏叹
调', '海的呢喃', '星序协响', '裁春', '直至海水褪色', '徘徊迷宫尽处', '映海之梦', '于静谧呢喃', '燃焰于海', '炽羽策阵星', ' 和光回唱', '不灭航路', '赫奕流明', '另一种喧嚣', '附彩作长吟', '箱中舞台', '寒尽觉春生', '死与舞', '琼枝冰绡', '悲喜剧', ' 时和岁稔', '惊庭雨时节', '千机逐星野', '掣傀之手', '诸方玄枢', '夜将寒色去', '苍鳞千嶂']

pool_by_ver: ['胜利为我喝彩', '焰痕', '却也在风潮后轻舞', '不屈命定之冠']

info: {'type': 'character', '4': ['SANHUA', 'BAIZHI', 'CHIXIA'], '5': 'LUPA'}

prize_pool: {'type': 'character', '3': ['源能长刃·测壹', '源能迅刀·测贰', '源能佩枪·测叁', '源能臂铠·测肆', '源能音感仪·测 五', '远行者长刃·辟路', '远行者迅刀·旅迹', '远行者佩枪·洞察', '远行者臂铠·破障', '远行者矩阵·探幽', '暗夜长刃·玄明', '暗夜 迅刀·黑闪', '暗夜佩枪·暗星', '暗夜臂铠·夜芒', '暗夜矩阵·暝光'], '4': {'up': ['SANHUA', 'BAIZHI', 'CHIXIA'], 'normal': ['不 归孤军', '东落', '今州守望', '凋亡频移', '华彩乐段', '呼啸重音', '奇幻变奏', '尘云旋臂', '异响空灵', '异度', '悖论喷流', ' 无眠烈火', '核熔星盘', '永夜长明', '永续坍缩', '行进序曲', '袍泽之固', '西升', '飞逝', '骇行', 'YANGYANG', 'YOUHU', 'LUMI', 'TAOQI', 'YUANWU', 'MORTEFI', 'AALTO', 'DANJIN']}, '5': {'up': 'LUPA', 'normal': ['CALCHARO', 'JIANXIN', 'VERINA', 'LINGYANG', 'ENCORE']}}

name: 露帕
'''
```