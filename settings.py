class Settings:
    """存储游戏《外星人入侵》中所有设置的类"""

    def __init__(self):
        """初始化游戏的静态设置"""
        # 屏幕设置
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # 飞船设置
        self.ship_speed = 0.7
        self.ship_limit = 3

        # 子弹设置
        self.bullet_speed = 0.45
        self.bullet_width = 10
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 3

        # 外星人设置
        self.alien_speed = 0.225
        self.fleet_drop_speed =10
        # fleet_direction为1表示向右移，为-1表示向左移
        self.fleet_direction = 1

        # 加快游戏节奏的速度
        self.speedup_scale = 1.25
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行而变化的设置"""
        self.ship_speed = 1.0
        self.bullet_speed = 1.0
        self.alien_speed =0.135

        # 记分
        self.alien_points = 50

        # fleet_direction为1 表示向右，为-1 表示向左
        self.fleet_direction = 1

    def increase_speed(self):

        self.ship_speed *= 1.1
        self.bullet_speed *= 1.1
        self.alien_speed *= self.speedup_scale
