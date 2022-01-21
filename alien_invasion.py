import sys

import pygame

from time import sleep

from settings import Settings

from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        pygame.mixer.music.load('music/gamebgm.mp3')
        pygame.mixer.music.play(-1)  # 重复播放音乐
        self.settings = Settings()

        # 全屏游戏代码：
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        # 小屏游戏代码：
        # self.screen = pygame.display.set_mode(
        #   (self.settings.screen_width, self.settings.screen_height))

        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 设置背景色
        self.bg_color = (666, 666, 666)

        # 创建Play按钮
        self.play_button = Button(self, "Play")

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # KEYDOWN：当用户按下键盘上的任意按键时触发
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                # KEYUP：当用户释放键盘上的按键时触发
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """在玩家单击Play按钮时开始游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # 重置游戏设置
            self.settings.initialize_dynamic_settings()
            # 隐藏鼠标光标
            pygame.mouse.set_visible(False)
            # 重置游戏统计信息
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人并让飞船居中
            self._create_fleet()
            self.ship.center_ship()

    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.KEYUP:
            self.ship.moving_up = True
        elif event.key == pygame.KEYDOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_ESCAPE:
            # 按esc键退出游戏窗口
            sys.exit()
        elif event.key == pygame.K_SPACE:
            # 播放发射子弹音效
            # 注意：声音会有一定的延迟
            pygame.mixer.init()
            sound = pygame.mixer.Sound('music/hit.wav')
            sound.play()
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):
        """创建一颗子弹，并将其加入编组bullets中"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        # 更新子弹的位置
        self.bullets.update()
        # 删除消失的子弹
        for bullet in self.bullets.copy():
            # 这里遍历的是bullets的副本，因为不是副本的话，每删除一次，列表中的元素都会往前移，
            # 而指针往后移，于是会因下标不一致而导致漏删，最终无法有序删除子弹
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets)) 核实是否删除子弹成功

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """
        响应子弹和外星人碰撞
        删除发生碰撞的子弹和外星人
        """

        # 检查是否有子弹击中了外星人
        # 如果是，就删除相应的子弹和外星人
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            # self.stats.score += self.settings.alien_points 这段代码可能导致一个子弹同时击中多个外星人，只得到一个外星人的分数
            # 所以用下面代码
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # 删除现有的子弹弄新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _create_fleet(self):
        """创建外星人群"""
        # 创建一个外星人并计算一行可容纳多少个外星人
        # 外星人的间距为外星人宽度
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size  # 用属性size直接获取外星人宽度和高度
        available_space_x = self.settings.screen_width - (2 * alien_width)  # 计算一行屏幕容纳外星人的容量
        number_aliens_x = available_space_x // (2 * alien_width)  # 计算一行可容纳多少个外星人

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # 创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其加入当前行"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人下移，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """
        检查是否有外星人位于屏幕边缘
        并更新整群外星人的位置
        """
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星人与飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 检测是否有外星人到达了屏幕的底端
        self._check_aliens_bottom()

    def _ship_hit(self):
        """响应飞船撞到外星人"""
        # 撞击音效
        pygame.mixer.init()
        sound = pygame.mixer.Sound('music/bomb.wav')
        sound.play()
        if self.stats.ships_left > 0:
            # 将ships_left减1并更新记分牌
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            # 创建一群新的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(1)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)   # 游戏结束，显示鼠标光标

    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕底端"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 像飞船与外星人相撞一样的结果
                self._ship_hit()
                break

    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        # 每次循环都时都重绘屏幕
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # 显示得分
        self.sb.show_score()

        # 如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        # 让最近绘制的屏幕可见
        pygame.display.flip()


if __name__ == '__main__':
    # "if __name__ == '__main__':"表示，仅当直接运行本文件时，以下函数才执行
    # 创建游戏实例并运行游戏
    ai = AlienInvasion()
    ai.run_game()
